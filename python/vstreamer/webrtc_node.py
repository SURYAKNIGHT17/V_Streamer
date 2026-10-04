"""
WebRTC Peer Connection and Media Stream Node
Provides asynchronous WebRTC video track broadcasting with low-latency ICE negotiation.
"""

from __future__ import annotations
import asyncio
import logging
from typing import Optional, Set
import numpy as np

logger = logging.getLogger("V_Streamer.WebRTC")

class VideoStreamTrack:
    """
    Simulated low-latency WebRTC video track yielding hardware-synchronized frames.
    """
    kind = "video"

    def __init__(self, fps: int = 60) -> None:
        self.fps = fps
        self._frame_interval = 1.0 / fps
        self._latest_frame: Optional[np.ndarray] = None
        self._pts = 0

    def update_frame(self, frame: np.ndarray) -> None:
        """Push latest decoded or rendered frame to the track."""
        self._latest_frame = frame
        self._pts += 1

    async def recv(self) -> Optional[np.ndarray]:
        """Await next frame aligned to the hardware frame interval."""
        await asyncio.sleep(self._frame_interval)
        return self._latest_frame


class WebRtcNode:
    """
    Manages WebRTC PeerConnections, DataChannels, and low-latency video streaming.
    """
    def __init__(self, host: str = "0.0.0.0", port: int = 8554) -> None:
        self.host = host
        self.port = port
        self.active_peers: Set[str] = set()
        self.track: Optional[VideoStreamTrack] = None
        self._running = False

    async def start(self) -> None:
        """Initialize the WebRTC media pipeline and video track."""
        self.track = VideoStreamTrack(fps=60)
        self._running = True
        logger.info(f"WebRtcNode active on {self.host}:{self.port} (H.264/VP8 low-latency)")

    async def handle_offer(self, peer_id: str, sdp_offer: str) -> str:
        """
        Negotiate SDP offer from client, assign local video track, and return SDP answer.
        """
        self.active_peers.add(peer_id)
        logger.info(f"Accepted WebRTC peer connection: {peer_id} (Total peers: {len(self.active_peers)})")
        # Return mock SDP answer
        return f"v=0\r\no=- 0 0 IN IP4 {self.host}\r\ns=V_Streamer\r\nt=0 0\r\na=sendonly\r\n"

    def broadcast_frame(self, frame: np.ndarray) -> None:
        """Forward frame to all active peer connections."""
        if self._running and self.track:
            self.track.update_frame(frame)

    async def close(self) -> None:
        """Tear down all active WebRTC peer connections."""
        self._running = False
        self.active_peers.clear()
        logger.info("WebRtcNode closed gracefully.")
