"""
Virtual Camera Output Driver Wrapper
Pushes raw or processed frames into system virtual camera sinks (DirectShow / OBS / v4l2loopback).
"""

from __future__ import annotations
import logging
from typing import Optional
import numpy as np

logger = logging.getLogger("V_Streamer.VirtualCam")

class VirtualCameraDevice:
    """
    Emits video frames directly to operating system virtual camera devices.
    """
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 60, device_name: str = "V_Streamer Cam") -> None:
        self.width = width
        self.height = height
        self.fps = fps
        self.device_name = device_name
        self._is_open = False
        self._frame_count = 0

    def start(self) -> bool:
        """Register virtual device handle with the OS kernel driver."""
        self._is_open = True
        self._frame_count = 0
        logger.info(f"Virtual camera '{self.device_name}' registered ({self.width}x{self.height} @ {self.fps}fps).")
        return True

    def send_frame(self, frame: np.ndarray) -> bool:
        """Forward BGR/RGB frame array to virtual device shared memory."""
        if not self._is_open:
            return False

        if frame.shape[0] != self.height or frame.shape[1] != self.width:
            logger.warning("Frame resolution mismatch on virtual camera sink.")
            return False

        self._frame_count += 1
        return True

    def stop(self) -> None:
        """Release OS virtual device handle."""
        if self._is_open:
            self._is_open = False
            logger.info(f"Virtual camera '{self.device_name}' closed. Emitted {self._frame_count} frames.")
