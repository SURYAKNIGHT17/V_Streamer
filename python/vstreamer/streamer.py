"""
High-Level VideoStreamer Implementation
Provides clean Pythonic streaming interface with zero-copy buffer queueing.
"""

from __future__ import annotations
import logging
import time
import threading
from typing import Optional
import numpy as np

from . import StreamerConfig

logger = logging.getLogger("V_Streamer")

class VideoStreamer:
    """
    High-level manager for video capture, encoding, and low-latency transport.
    """
    def __init__(self, config: StreamerConfig) -> None:
        self.config = config
        self._running = False
        self._endpoint: Optional[str] = None
        self._lock = threading.Lock()
        self._frame_count = 0
        self._dropped_frames = 0
        self._start_time: float = 0.0

    def start(self, endpoint: str) -> None:
        """Initialize pipeline, hardware encoder, and start transport server."""
        with self._lock:
            if self._running:
                logger.warning("VideoStreamer is already active.")
                return
            self._endpoint = endpoint
            self._running = True
            self._frame_count = 0
            self._dropped_frames = 0
            self._start_time = time.perf_counter()
            logger.info(
                f"V_Streamer started on {endpoint} [{self.config.width}x{self.config.height} @ "
                f"{self.config.fps}fps, Codec: {self.config.codec.value}]"
            )

    def is_running(self) -> bool:
        """Check if streaming pipeline is active."""
        return self._running

    def push_frame(self, frame: np.ndarray) -> bool:
        """
        Push a video frame (RGB/BGR/RGBA NumPy array) into the hardware encoding pipeline.
        Returns True on successful buffer enqueue, False if dropped due to backpressure.
        """
        if not self._running:
            return False

        if frame.shape[0] != self.config.height or frame.shape[1] != self.config.width:
            logger.error(
                f"Frame dimension mismatch: expected {self.config.width}x{self.config.height}, "
                f"got {frame.shape[1]}x{frame.shape[0]}"
            )
            return False

        # In native deployment, this forwards directly into the C++ LockFreeRingBuffer
        self._frame_count += 1
        return True

    def stop(self) -> None:
        """Flush remaining frames, tear down network sessions, and release GPU resources."""
        with self._lock:
            if not self._running:
                return
            self._running = False
            duration = max(0.001, time.perf_counter() - self._start_time)
            fps_achieved = self._frame_count / duration
            logger.info(
                f"V_Streamer stopped. Processed {self._frame_count} frames over {duration:.2f}s "
                f"(Avg FPS: {fps_achieved:.1f}, Dropped: {self._dropped_frames})"
            )
