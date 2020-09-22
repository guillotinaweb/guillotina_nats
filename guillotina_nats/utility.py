# -*- coding: utf-8 -*-
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed
from nats.aio.errors import ErrConnectionReconnecting
from nats.aio.errors import ErrNoServers
from nats.aio.errors import ErrTimeout
from stan.aio.client import Client as STAN
from stan.aio.errors import StanError

import asyncio
import logging
import os
import uuid

logger = logging.getLogger("guillotina_nats")


# Configuration Utility


class NatsUtility(object):
    def __init__(self, settings, loop=None):
        self._loop = loop
        self._hosts = settings["hosts"]
        self._timeout = float(settings["timeout"])
        self._subscriptions = []
        self._stream_subscriptions = []
        self._stan = settings.get("stan", None)
        self._name = settings.get("name", None)
        self._thread = settings.get("thread", False)
        self._uuid = os.environ.get("HOSTNAME", uuid.uuid4().hex)
        self._initialized = False
        self.lock = asyncio.Lock()
        self.sc = None
        self.nc = None

    async def subscribe(self, handler, key, group=""):
        if self.nc.is_connected:
            sid = await self.nc.subscribe(key, queue=group, cb=handler)
            self._subscriptions.append(sid)
            logger.info("Subscribed to " + key)
            return sid
        else:
            raise ErrConnectionClosed("Could not subscribe")

    async def unsubscribe(self, sid):
        if self.nc.is_connected and sid is not None:
            await self.nc.unsubscribe(sid)
            self._subscriptions.remove(sid)
        else:
            raise ErrConnectionClosed("Could not unsubscribe")

    async def stream_subscribe(self, handler, key, **params):
        if self.sc._conn_id:
            sid = await self.sc.subscribe(key, cb=handler, **params)
            self._stream_subscriptions.append(sid)
            logger.info("Subscribed to " + key)
            return sid
        else:
            raise ErrConnectionClosed("Could not subscribe")

    async def stream_unsubscribe(self, sid):
        if self.sc._conn_id:
            await sid.unsubscribe()
            self._stream_subscriptions.remove(sid)
        else:
            raise ErrConnectionClosed("Could not unsubscribe")

    async def publish(self, key, value):
        if self.nc.is_connected:
            await self.nc.publish(key, value)
        else:
            raise ErrConnectionClosed("Could not publish")

    async def stream_publish(self, key, value):
        async def cb(ack):
            pass

        try:
            await self.sc.publish(key, value, ack_handler=cb, ack_wait=60)
        except AttributeError:
            await self.sc.connect(self._stan, self._uuid, nats=self.nc)
            await asyncio.sleep(2)
            await self.sc.publish(key, value, ack_handler=cb, ack_wait=60)

    async def request(self, key, value, timeout=None):
        if timeout is None:
            timeout = self._timeout
        if self.nc.is_connected:
            try:
                return await self.nc.request(key, value, timeout)
            except ErrTimeout:
                return
        else:
            raise ErrConnectionClosed("Could not subscribe")

    async def stream(self, channel_name, data):
        if self.sc._conn_id:
            await self.sc.publish(channel_name, data)
        else:
            raise ErrConnectionClosed("Could not publish")

    async def initialized(self):
        if self._initialized:
            return True
        async with self.lock:
            return True
        return False

    async def initialize(self, app=None):
        # No asyncio loop to run
        async with self.lock:
            self.nc = NATS()
            options = {
                "servers": self._hosts,
                "loop": self._loop,
                "disconnected_cb": self.disconnected_cb,
                "reconnected_cb": self.reconnected_cb,
                "error_cb": self.error_cb,
                "closed_cb": self.closed_cb,
                "name": self._name,
                "verbose": True,
            }

            try:
                await self.nc.connect(**options)
            except ErrNoServers:
                logger.exception("No servers found")
                raise

            logger.info("Connected to nats")

            if self._stan is not None:
                self.sc = STAN()
                await self.sc.connect(self._stan, self._uuid, nats=self.nc)
                logger.info("Connected to stan")
        self._initialized = True

    async def finalize(self, app):
        if self.sc:
            for sid in self._stream_subscriptions:
                await sid.unsubscribe()
            try:
                await self.sc.close()
            except ErrTimeout:
                pass
            except StanError:
                pass
        if self.nc:
            try:
                await self.nc.flush()
            except RuntimeError:
                pass
            for key in self._subscriptions:
                await self.nc.unsubscribe(key)
            try:
                await self.nc.drain()
            except AttributeError:
                pass
            except ErrConnectionReconnecting:
                pass
            try:
                await self.nc.close()
            except RuntimeError:
                pass

    async def disconnected_cb(self):
        logger.info("Got disconnected!")

    async def reconnected_cb(self):
        # See who we are connected to on reconnect.
        logger.info("Got reconnected to {url}".format(url=self.nc.connected_url.netloc))

    async def error_cb(self, e):
        logger.info("There was an error: {}".format(e))

    async def closed_cb(self):
        logger.info("Connection is closed")
