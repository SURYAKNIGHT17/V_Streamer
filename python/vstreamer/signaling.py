"""
WebSocket Signaling Server for WebRTC Negotiation
Handles client registration, SDP exchange, and ICE candidate relay.
"""

from __future__ import annotations
import json
import logging
from typing import Dict, Callable, Any

logger = logging.getLogger("V_Streamer.Signaling")

class SignalingServer:
    """
    Lightweight signaling router for WebRTC session initiation.
    """
    def __init__(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        self.host = host
        self.port = port
        self.routes: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def register_handler(self, msg_type: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """Register a handler for specific signaling message types (e.g. 'offer', 'candidate')."""
        self.routes[msg_type] = handler

    def process_message(self, raw_json: str) -> str:
        """Parse incoming JSON payload and dispatch to registered signaling handler."""
        try:
            data = json.loads(raw_json)
            msg_type = data.get("type", "unknown")
            if msg_type in self.routes:
                response = self.routes[msg_type](data)
                return json.dumps(response)
            return json.dumps({"status": "error", "message": f"Unsupported type: {msg_type}"})
        except Exception as e:
            logger.error(f"Signaling dispatch error: {e}")
            return json.dumps({"status": "error", "message": str(e)})
