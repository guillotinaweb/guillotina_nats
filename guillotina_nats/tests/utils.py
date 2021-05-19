import http.client
import json
import os
import random
import signal
import subprocess
import time


class Gnatsd(object):
    def __init__(
        self,
        port=4222,
        user="",
        password="",
        token="",
        timeout=0,
        http_port=8222,
        debug=False,
        tls=False,
        cluster_listen=None,
        routes=[],
        config_file=None,
    ):
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.http_port = http_port
        self.proc = None
        self.debug = debug
        self.tls = tls
        self.token = token
        self.cluster_listen = cluster_listen
        self.routes = routes
        self.bin_name = "gnatsd"
        self.config_file = config_file

        env_debug_flag = os.environ.get("DEBUG_NATS_TEST")
        if env_debug_flag == "true":
            self.debug = True

    def start(self):
        cmd = [
            f"{self.path}/{self.bin_name}",
            "-js",
            "-p",
            "%d" % self.port,
            "-m",
            "%d" % self.http_port,
            "-a",
            "127.0.0.1",
        ]
        if self.user != "":
            cmd.append("--user")
            cmd.append(self.user)
        if self.password != "":
            cmd.append("--pass")
            cmd.append(self.password)

        if self.token != "":
            cmd.append("--auth")
            cmd.append(self.token)

        if self.debug:
            cmd.append("-DV")

        if self.tls:
            cmd.append("--tls")
            cmd.append("--tlscert")
            cmd.append("tests/certs/server-cert.pem")
            cmd.append("--tlskey")
            cmd.append("tests/certs/server-key.pem")
            cmd.append("--tlsverify")
            cmd.append("--tlscacert")
            cmd.append("tests/certs/ca.pem")

        if self.cluster_listen is not None:
            cmd.append("--cluster_listen")
            cmd.append(self.cluster_listen)

        if len(self.routes) > 0:
            cmd.append("--routes")
            cmd.append(",".join(self.routes))

        if self.config_file is not None:
            cmd.append("--config")
            cmd.append(self.config_file)

        if self.debug:
            self.proc = subprocess.Popen(cmd)
        else:
            self.proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        if self.debug:
            if self.proc is None:
                print(
                    "[\031[0;33mDEBUG\033[0;0m] Failed to start server listening on port %d started."
                    % self.port
                )
            else:
                print(
                    "[\033[0;33mDEBUG\033[0;0m] Server listening on port %d started."
                    % self.port
                )
        return self.proc

    def stop(self):
        if self.debug:
            print(
                "[\033[0;33mDEBUG\033[0;0m] Server listening on %d will stop."
                % self.port
            )

        if self.debug:
            if self.proc is None:
                print(
                    "[\033[0;31mDEBUG\033[0;0m] Failed terminating server listening on port %d"
                    % self.port
                )

        if self.proc.returncode is not None:
            if self.debug:
                print(
                    "[\033[0;31mDEBUG\033[0;0m] Server listening on port {port} finished running already with exit {ret}".format(
                        port=self.port, ret=self.proc.returncode
                    )
                )
        else:
            os.kill(self.proc.pid, signal.SIGKILL)
            self.proc.wait()
            if self.debug:
                print(
                    "[\033[0;33mDEBUG\033[0;0m] Server listening on %d was stopped."
                    % self.port
                )


class NatsServer(Gnatsd):
    def __init__(self):
        super(Gnatsd, self)
        self.bin_name = "nats-server"


def start_gnatsd(gnatsd: Gnatsd):
    gnatsd.start()

    endpoint = "127.0.0.1:{port}".format(port=gnatsd.http_port)
    retries = 0
    while True:
        if retries > 100:
            break

        try:
            httpclient = http.client.HTTPConnection(endpoint, timeout=5)
            httpclient.request("GET", "/varz")
            response = httpclient.getresponse()
            if response.status == 200:
                break
        except:
            retries += 1
            time.sleep(0.1)


class StanServer(object):
    def __init__(
        self,
        port=4222,
        user="",
        password="",
        token="",
        timeout=0,
        http_port=8222,
        debug=False,
        tls=False,
        cluster_listen=None,
        routes=[],
    ):
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.http_port = http_port
        self.proc = None
        self.debug = debug
        self.tls = tls
        self.token = token
        self.cluster_listen = cluster_listen
        self.routes = routes

        env_debug_flag = os.environ.get("DEBUG_NATS_TEST")
        if env_debug_flag == "true":
            self.debug = True

    def start(self):
        cmd = [
            f"{self.path}/nats-streaming-server",
            "-p",
            "%d" % self.port,
            "-m",
            "%d" % self.http_port,
            "-a",
            "127.0.0.1",
        ]
        if self.user != "":
            cmd.append("--user")
            cmd.append(self.user)
        if self.password != "":
            cmd.append("--pass")
            cmd.append(self.password)

        if self.token != "":
            cmd.append("--auth")
            cmd.append(self.token)

        if self.debug:
            cmd.append("-SDV")
            cmd.append("-DV")

        if self.cluster_listen is not None:
            cmd.append("--cluster_listen")
            cmd.append(self.cluster_listen)

        if len(self.routes) > 0:
            cmd.append("--routes")
            cmd.append(",".join(self.routes))

        if self.debug:
            self.proc = subprocess.Popen(cmd)
        else:
            self.proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        if self.debug:
            if self.proc is None:
                print(
                    "[\031[0;33mDEBUG\033[0;0m] Failed to start server listening on port %d started."
                    % self.port
                )
            else:
                print(
                    "[\033[0;33mDEBUG\033[0;0m] Server listening on port %d started."
                    % self.port
                )
        return self.proc

    def stop(self):
        if self.debug:
            print(
                "[\033[0;33mDEBUG\033[0;0m] Server listening on %d will stop."
                % self.port
            )

        if self.debug:
            if self.proc is None:
                print(
                    "[\033[0;31mDEBUG\033[0;0m] Failed terminating server listening on port %d"
                    % self.port
                )

        if self.proc.returncode is not None:
            if self.debug:
                print(
                    "[\033[0;31mDEBUG\033[0;0m] Server listening on port {port} finished running already with exit {ret}".format(
                        port=self.port, ret=self.proc.returncode
                    )
                )
        else:
            os.kill(self.proc.pid, signal.SIGKILL)
            self.proc.wait()
            if self.debug:
                print(
                    "[\033[0;33mDEBUG\033[0;0m] Server listening on %d was stopped."
                    % self.port
                )


def start_nats_streaming(server: StanServer):
    server.start()

    endpoint = "127.0.0.1:{port}".format(port=server.http_port)
    retries = 0
    while True:
        if retries > 100:
            break

        try:
            httpclient = http.client.HTTPConnection(endpoint, timeout=5)
            httpclient.request("GET", "/subsz")
            response = httpclient.getresponse()
            if response.status == 200:
                # Check that at least the minimum subjects for a
                # NATS Streaming session are ready.
                connz = json.loads(response.read())
                if connz["num_subscriptions"] < 7:
                    continue
                else:
                    break
        except:
            retries += 1
            time.sleep(0.1)


def generate_client_id():
    return "%x" % random.SystemRandom().getrandbits(0x58)
