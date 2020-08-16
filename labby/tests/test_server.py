import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch

from labby.server import Client, HaltRequest, Server, ServerRequest


FAKE_PID = 42


class ServerTest(TestCase):
    @patch("os.fork", return_value=FAKE_PID)
    def test_parent_process_on_start(self, _fork_mock: MagicMock) -> None:
        server = Server()
        server_info = server.start()
        self.assertFalse(server_info.existing)
        self.assertEquals(server_info.pid, FAKE_PID)

    @patch("os.fork", return_value=0)
    @patch("labby.server.Rep0")
    def test_child_process_on_start(
        self, rep0_mock: MagicMock, _fork_mock: MagicMock
    ) -> None:
        rep0_mock.return_value.__enter__.return_value.recv.return_value = (
            HaltRequest().to_msgpack()
        )

        server = Server()
        with self.assertRaises(SystemExit):
            server.start()


class ClientTest(TestCase):
    req_patch: unittest.mock._patch
    req_mock: MagicMock
    client: Client

    def setUp(self) -> None:
        self.req_patch = patch("labby.server.Req0")
        self.req_mock = self.req_patch.start()
        self.req_mock.return_value.send.side_effect = ServerRequest.handle_from_msgpack

        self.client = Client("foobar")

    def tearDown(self) -> None:
        self.req_patch.stop()

    def test_halt(self) -> None:
        with self.assertRaises(SystemExit):
            self.client.halt()

    def test_close(self) -> None:
        self.client.close()
        self.req_mock.return_value.close.assert_called_once()
