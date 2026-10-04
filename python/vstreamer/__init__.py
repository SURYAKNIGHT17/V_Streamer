"""
V_Streamer Python Package
Ultra-low-latency, hardware-accelerated video streaming and virtual device engine.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional

__version__ = "1.0.0"

class CodecType(str, Enum):
    H264_NVENC = "h264_nvenc"
    HEVC_NVENC = "hevc_nvenc"
    AV1_NVENC = "av1_nvenc"
    LIBX264 = "libx264"

class TransportProtocol(str, Enum):
    WEBRTC = "webrtc"
    SRT = "srt"
    RTMP = "rtmp"
    SHARED_MEMORY = "shm"

@dataclass
class StreamerConfig:
    width: int = 1920
    height: int = 1080
    fps: int = 60
    bitrate_kbps: int = 6000
    codec: CodecType = CodecType.H264_NVENC
    protocol: TransportProtocol = TransportProtocol.WEBRTC
    enable_virtual_cam: bool = True
    zero_copy: bool = True

from .streamer import VideoStreamer

__all__ = [
    "CodecType",
    "TransportProtocol",
    "StreamerConfig",
    "VideoStreamer",
    "__version__"
]
