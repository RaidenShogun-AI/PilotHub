"""
NeoCortex Provider
Interconnects PilotHub with the NeoCortex local-first AI intelligence layer.
Supports both native AF_UNIX IPC protocol framing and HTTP fallback.
"""
import json
import os
import socket
import struct
import uuid
from pathlib import Path
from typing import Optional

import requests

from base_provider import AIProvider


class NeoCortexProvider(AIProvider):
    """NeoCortex intelligence layer provider for PilotHub"""

    def __init__(
        self,
        socket_path: Optional[str] = None,
        http_endpoint: Optional[str] = None,
        timeout: float = 10.0
    ):
        super().__init__(api_key="")
        
        # Resolve socket path: check custom, XDG_RUNTIME_DIR, or fallback
        if socket_path:
            self.socket_path = Path(socket_path)
        else:
            runtime_dir = os.getenv("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
            self.socket_path = Path(runtime_dir) / "neocortex" / "core.sock"

        self.http_endpoint = http_endpoint or os.getenv("NEOCORTEX_ENDPOINT", "http://127.0.0.1:11434")
        self.timeout = timeout

    def _send_frame(self, sock: socket.socket, message_kind: str, body: dict) -> None:
        """Send a length-prefixed protocol frame to NeoCortex IPC"""
        envelope = {
            "protocol": 1,
            "request_id": str(uuid.uuid4()),
            "kind": message_kind,
            "body": body
        }
        payload = json.dumps(envelope).encode("utf-8")
        header = struct.pack(">I", len(payload))
        sock.sendall(header + payload)

    def _read_frame(self, sock: socket.socket) -> dict:
        """Read a single length-prefixed protocol frame from NeoCortex IPC"""
        header = sock.recv(4)
        if len(header) < 4:
            raise ConnectionError("Connection closed before frame length was received")
        frame_len = struct.unpack(">I", header)[0]

        chunks = []
        bytes_read = 0
        while bytes_read < frame_len:
            chunk = sock.recv(min(frame_len - bytes_read, 65536))
            if not chunk:
                raise ConnectionError("Connection closed prematurely while reading frame body")
            chunks.append(chunk)
            bytes_read += len(chunk)

        payload = b"".join(chunks).decode("utf-8")
        return json.loads(payload)

    def _query_unix_socket(self, text: str) -> str:
        """Communicate with neocortex-core via AF_UNIX socket"""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect(str(self.socket_path))
            
            # 1. Handshake
            self._send_frame(sock, "hello", {
                "component": "pilothub",
                "version": "1.0.0"
            })
            hello_resp = self._read_frame(sock)
            if hello_resp.get("kind") != "hello.ok":
                return f"NeoCortex handshake failed: {hello_resp}"

            # 2. Send User Message
            self._send_frame(sock, "user.message", {"text": text})

            # 3. Read stream deltas until completion
            accumulated_text = []
            while True:
                frame = self._read_frame(sock)
                kind = frame.get("kind")
                body = frame.get("body", {})

                if kind == "assistant.delta":
                    delta = body.get("text", "")
                    accumulated_text.append(delta)
                elif kind == "assistant.done":
                    break
                elif kind == "error":
                    err_msg = body.get("message", "Unknown error")
                    return f"NeoCortex protocol error: {err_msg}"
                elif kind == "action.result":
                    # Tool action completed
                    result_msg = body.get("result", "")
                    if result_msg:
                        accumulated_text.append(f"\n[Tool Result]: {result_msg}")

            return "".join(accumulated_text) or "NeoCortex completed response with no text output."
        finally:
            sock.close()

    def _query_http(self, text: str) -> str:
        """Fallback to HTTP endpoint if NeoCortex is configured via HTTP proxy"""
        url = f"{self.http_endpoint.rstrip('/')}/api/generate"
        payload = {
            "model": "qwen2.5-coder-3b",
            "prompt": text,
            "stream": False
        }
        resp = requests.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", data.get("message", {}).get("content", str(data)))

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from NeoCortex intelligence layer"""
        # Try native Unix socket first
        if self.socket_path.exists():
            try:
                return self._query_unix_socket(prompt)
            except Exception as e:
                return f"Error communicating with NeoCortex socket ({self.socket_path}): {e}"

        # Otherwise try HTTP fallback if accessible
        try:
            return self._query_http(prompt)
        except Exception:
            return (
                f"NeoCortex is not active. Socket not found at {self.socket_path} "
                f"and HTTP endpoint ({self.http_endpoint}) is unreachable. "
                "To interconnect, start neocortex-core daemon."
            )

    def chat(self, messages: list, **kwargs) -> str:
        """Chat with NeoCortex with conversation context"""
        # Format conversation messages for NeoCortex
        if not messages:
            return ""
        
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        return self.generate_text(last_user_msg, **kwargs)
