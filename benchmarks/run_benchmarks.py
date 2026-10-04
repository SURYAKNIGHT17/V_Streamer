"""
V_Streamer Benchmark Runner
Executes synthetic video frame loops and calculates throughput, encode timing, and RSS memory usage.
"""

from __future__ import annotations
import os
import sys
import time
import json
import psutil
import numpy as np

# Adjust import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python")))

from vstreamer import StreamerConfig, VideoStreamer, CodecType, TransportProtocol

def run_benchmark(width=1920, height=1080, fps=60, duration_sec=5):
    print(f"=== Running V_Streamer Benchmark: {width}x{height} @ {fps}fps ({duration_sec}s) ===")
    process = psutil.Process(os.getpid())
    init_rss = process.memory_info().rss / (1024 * 1024)

    config = StreamerConfig(
        width=width,
        height=height,
        fps=fps,
        bitrate_kbps=6000,
        codec=CodecType.H264_NVENC,
        protocol=TransportProtocol.WEBRTC
    )

    streamer = VideoStreamer(config)
    streamer.start("benchmark://null")

    frame = np.zeros((height, width, 3), dtype=np.uint8)
    total_frames = fps * duration_sec
    frame_interval = 1.0 / fps

    latencies = []
    start_time = time.perf_counter()

    for _ in range(total_frames):
        t0 = time.perf_counter()
        streamer.push_frame(frame)
        t_elapsed = time.perf_counter() - t0
        latencies.append(t_elapsed * 1000.0)

        # Rate limiter
        sleep_dur = frame_interval - t_elapsed
        if sleep_dur > 0:
            time.sleep(sleep_dur)

    end_time = time.perf_counter()
    peak_rss = process.memory_info().rss / (1024 * 1024)
    streamer.stop()

    actual_duration = end_time - start_time
    avg_fps = total_frames / actual_duration
    p50 = float(np.percentile(latencies, 50))
    p95 = float(np.percentile(latencies, 95))
    p99 = float(np.percentile(latencies, 99))

    print(f"  Processed Frames : {total_frames}")
    print(f"  Achieved FPS     : {avg_fps:.2f}")
    print(f"  Latency P50      : {p50:.3f} ms")
    print(f"  Latency P99      : {p99:.3f} ms")
    print(f"  Initial RSS Mem  : {init_rss:.1f} MB")
    print(f"  Peak RSS Mem     : {peak_rss:.1f} MB")
    print("====================================================================\n")

if __name__ == "__main__":
    run_benchmark(1920, 1080, 60, 3)
