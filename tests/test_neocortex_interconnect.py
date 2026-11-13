import json
import socket
import struct
import unittest
from unittest.mock import MagicMock, patch

from neocortex_provider import NeoCortexProvider
from web_app import app, chatbot as global_bot, get_chatbot
from chatbot import UnifiedAIChatbot


class TestNeoCortexInterconnect(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        import web_app
        web_app.chatbot = UnifiedAIChatbot()

    def test_neocortex_provider_offline_message(self):
        provider = NeoCortexProvider(socket_path="/nonexistent/sock/path.sock", http_endpoint="http://127.0.0.1:99999")
        response = provider.generate_text("Hello NeoCortex")
        self.assertIn("NeoCortex is not active", response)

    @patch('socket.socket')
    def test_neocortex_socket_protocol(self, mock_socket_class):
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock

        # Mock hello.ok response frame
        hello_ok = {
            "protocol": 1,
            "request_id": "req-1",
            "kind": "hello.ok",
            "body": {"component": "neocortex-core", "version": "0.1.0"}
        }
        hello_bytes = json.dumps(hello_ok).encode("utf-8")
        hello_frame = struct.pack(">I", len(hello_bytes)) + hello_bytes

        # Mock assistant.delta response frame
        delta_body = {
            "protocol": 1,
            "request_id": "req-2",
            "kind": "assistant.delta",
            "body": {"text": "NeOS intelligence online."}
        }
        delta_bytes = json.dumps(delta_body).encode("utf-8")
        delta_frame = struct.pack(">I", len(delta_bytes)) + delta_bytes

        # Mock assistant.done response frame
        done_body = {
            "protocol": 1,
            "request_id": "req-3",
            "kind": "assistant.done",
            "body": {}
        }
        done_bytes = json.dumps(done_body).encode("utf-8")
        done_frame = struct.pack(">I", len(done_bytes)) + done_bytes

        all_incoming = hello_frame + delta_frame + done_frame
        idx = 0

        def fake_recv(n):
            nonlocal idx
            chunk = all_incoming[idx:idx + n]
            idx += len(chunk)
            return chunk

        mock_sock.recv.side_effect = fake_recv

        provider = NeoCortexProvider(socket_path="/tmp/fake_neocortex.sock")
        with patch('pathlib.Path.exists', return_value=True):
            resp = provider.generate_text("Run diagnostics")
            self.assertEqual(resp, "NeOS intelligence online.")

    def test_openai_compatible_models_endpoint(self):
        res = self.app.get('/v1/models')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("object"), "list")
        model_ids = [m["id"] for m in data.get("data", [])]
        self.assertIn("neocortex", model_ids)

    def test_openai_compatible_chat_completions(self):
        res = self.app.post('/v1/chat/completions', json={
            "model": "duckduckgo",
            "messages": [{"role": "user", "content": "Hello"}]
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("object"), "chat.completion")
        self.assertTrue(len(data.get("choices", [])) > 0)


if __name__ == '__main__':
    unittest.main()
