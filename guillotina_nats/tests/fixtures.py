from guillotina import testing
from guillotina_nats.tests.utils import Gnatsd
from guillotina_nats.tests.utils import StanServer
from guillotina_nats.tests.utils import start_gnatsd
from guillotina_nats.tests.utils import start_nats_streaming
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

import os
import platform
import pytest


def base_settings_configurator(settings):
    if "applications" in settings:
        settings["applications"].append("guillotina_nats")
    else:
        settings["applications"] = ["guillotina_nats"]

    settings["load_utilities"]["nats"] = {
        "provides": "guillotina_nats.interfaces.INatsUtility",
        "factory": "guillotina_nats.utility.NatsUtility",
        "settings": {"timeout": 0.2, "hosts": ["nats://localhost:4222"], "stan": None},
    }


testing.configure_with(base_settings_configurator)


@pytest.fixture(scope="function")
def natsd():
    if not os.path.isfile("nats-server"):
        version = "v2.2.4"
        arch = platform.machine()
        if arch == "x86_64":
            arch = "amd64"
        system = platform.system().lower()

        url = f"https://github.com/nats-io/nats-server/releases/download/{version}/nats-server-{version}-{system}-{arch}.zip"

        resp = urlopen(url)
        zipfile = ZipFile(BytesIO(resp.read()))

        file = zipfile.open(f"nats-server-{version}-{system}-{arch}/nats-server")
        content = file.read()
        with open("nats-server", "wb") as f:
            f.write(content)
        os.chmod("nats-server", 755)

    server = Gnatsd(port=4222)
    server.bin_name = "nats-server"
    server.path = os.getcwd()
    start_gnatsd(server)
    print("Started natsd")
    yield
    server.stop()


@pytest.fixture(scope="function")
def stand():
    if not os.path.isfile("nats-streaming-server"):
        version = "v0.16.2"
        arch = platform.machine()
        if arch == "x86_64":
            arch = "amd64"
        system = platform.system().lower()

        url = f"https://github.com/nats-io/nats-streaming-server/releases/download/{version}/nats-streaming-server-{version}-{system}-{arch}.zip"

        resp = urlopen(url)
        zipfile = ZipFile(BytesIO(resp.read()))

        file = zipfile.open(
            f"nats-streaming-server-{version}-{system}-{arch}/nats-streaming-server"
        )
        content = file.read()
        with open("nats-streaming-server", "wb") as f:
            f.write(content)
        os.chmod("nats-streaming-server", 755)

    server = StanServer(port=4222)
    server.path = os.getcwd()
    start_nats_streaming(server)
    print("Started stand")
    yield
    server.stop()
