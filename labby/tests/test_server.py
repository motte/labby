import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from typing import cast

from mashumaro.serializer.msgpack import EncodedData

from labby.config import Config
from labby.hw.core import auto_discover_drivers
from labby.server import (
    Client,
    DeviceStatus,
    HaltRequest,
    ListDevicesResponse,
    Server,
    ServerRequest,
)
from labby.tests.utils import labby_config


FAKE_PID = 42


LABBY_CONFIG_YAML = """
---
devices:
  - name: "virtual-power-supply"
    type: power_supply
    driver: labby.hw.virtual.power_supply.PowerSupply
    args:
      load_in_ohms: 5
  - name: "broken-power-supply"
    type: power_supply
    driver: labby.hw.virtual.power_supply.BrokenPowerSupply
    args:
      load_in_ohms: 5
"""


class ServerTest(TestCase):
    @patch("os.fork", return_value=FAKE_PID)
    def test_parent_process_on_start(self, _fork_mock: MagicMock) -> None:
        with labby_config(LABBY_CONFIG_YAML):
            server = Server()
            server_info = server.start()
            self.assertFalse(server_info.existing)
            self.assertEqual(server_info.pid, FAKE_PID)

    @patch("os.fork", return_value=0)
    @patch("labby.server.Rep0")
    def test_child_process_on_start(
        self, rep0_mock: MagicMock, _fork_mock: MagicMock
    ) -> None:
        with labby_config(LABBY_CONFIG_YAML):
            rep0_mock.return_value.__enter__.return_value.recv.return_value = (
                b"HaltRequest:" + cast(bytes, HaltRequest().to_msgpack())
            )

            server = Server()
            with self.assertRaises(SystemExit):
                server.start()


class ClientTest(TestCase):
    req_patch: unittest.mock._patch
    req_mock: MagicMock
    client: Client

    def setUp(self) -> None:
        auto_discover_drivers()
        self.config = Config(LABBY_CONFIG_YAML)

        def _handle(msg: EncodedData) -> None:
            response_bytes = ServerRequest.handle_from_msgpack(self.config, msg)
            self.req_mock.return_value.recv.return_value = response_bytes

        self.req_patch = patch("labby.server.Req0")
        self.req_mock = self.req_patch.start()
        self.req_mock.return_value.send.side_effect = _handle

        self.client = Client("foobar")

    def tearDown(self) -> None:
        self.req_patch.stop()

    def test_halt(self) -> None:
        with self.assertRaises(SystemExit):
            self.client.halt()

    def test_close(self) -> None:
        self.client.close()
        self.req_mock.return_value.close.assert_called_once()

    def test_hello(self) -> None:
        response = self.client.hello()
        self.assertEqual(response, "Hello world")

    def test_list_devices(self) -> None:
        response = self.client.list_devices()
        self.assertEqual(
            response,
            ListDevicesResponse(
                devices=[
                    DeviceStatus(name="virtual-power-supply", is_available=True),
                    DeviceStatus(
                        name="broken-power-supply",
                        is_available=False,
                        error_type="Exception",
                        error_message="Unavailable device",
                    ),
                ]
            ),
        )

    def test_device_info(self) -> None:
        self.client.device_info("virtual-power-supply")
        # TODO: handle unknown device (error)
        # TODO: handle multiple different types of devices
        # TODO: handle connection being okay and not okay
        #   - need to pass down error message
