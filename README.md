<div align="center">

# V_Streamer

**Ultra-Low-Latency, Hardware-Accelerated Video Pipeline, Transcoder & Virtual Device Engine**

[![CI Build](https://img.shields.io/github/actions/workflow/status/SURYAKNIGHT17/V_Streamer/ci-build.yml?branch=main&style=flat-square)](https://github.com/SURYAKNIGHT17/V_Streamer/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![C++ Standard](https://img.shields.io/badge/C%2B%2B-20-blue.svg?style=flat-square&logo=c%2B%2B)](https://en.wikipedia.org/wiki/C%2B%2B20)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-brightgreen.svg?style=flat-square&logo=python)](https://python.org)
[![NVENC Accelerated](https://img.shields.io/badge/NVIDIA-CUDA%20%2F%20NVENC-76B900.svg?style=flat-square&logo=nvidia)](https://developer.nvidia.com/nvidia-video-codec-sdk)

</div>

---

## Overview

**`V_Streamer`** is an enterprise-grade, high-throughput video streaming and transcoding engine engineered for scenarios requiring deterministic sub-100ms glass-to-glass latency. Built on a hybrid C++20 core with zero-copy Python bindings, it leverages NVIDIA NVENC/NVDEC hardware acceleration, lock-free ring buffer memory architectures, and native WebRTC/SRT pipelines to bridge interactive streaming software, virtual avatars, and broadcast ingest endpoints.

### Key Capabilities
- **Sub-100ms Glass-to-Glass Latency:** Optimized pipeline latency using memory-mapped buffers and hardware-direct encoding.
- **Hardware Acceleration:** Native NVENC/NVDEC support via the NVIDIA Video Codec SDK with seamless fallback to Intel QSV and software x264/x265.
- **Zero-Copy Memory Transport:** Shared memory ring buffers (`IPC` & `CUDA Host-to-Device`) eliminate heap allocations and host-GPU round-trips.
- **Virtual Camera Output:** Native support for DirectShow on Windows and `v4l2loopback` on Linux for direct integration into OBS Studio, Discord, and Zoom.
- **Dual-Surface API:** Complete C++20 low-level core and high-performance Python bindings (`pybind11`).

---

## Prerequisites

### Hardware Requirements
| Component | Minimum | Recommended |
|---|---|---|
| **CPU** | x86_64 quad-core (Intel 8th Gen / AMD Ryzen 2000) with AVX2 | 8+ physical cores with AVX-512 support |
| **GPU** | NVIDIA GeForce GTX 1060 (Pascal, NVENC Gen 6) | NVIDIA RTX 3060+ (Ampere / Ada Lovelace, dual-NVENC) |
| **RAM** | 8 GB DDR4 | 16 GB+ Dual-Channel DDR4/DDR5 |
| **Storage** | 500 MB free disk space | NVMe PCIe Gen 4 SSD |

### Software Dependencies
- **Operating Systems:**
  - Linux: Ubuntu 22.04 LTS / 24.04 LTS, Arch Linux (Kernel $\ge 5.15$)
  - Windows: Windows 10 (64-bit Build 19041+) or Windows 11
- **Compilers:** GCC 11+, Clang 14+, or MSVC 2022 (v143+) with C++20 support
- **NVIDIA Ecosystem:** NVIDIA Display Driver $\ge 535.86$, CUDA Toolkit $\ge 12.0$, NVIDIA Video Codec SDK 12.1+
- **Build Tools:** CMake $\ge 3.22$, Ninja, Python $\ge 3.10$, FFmpeg $\ge 6.0$ development headers

---

## Installation

### 1. Clone the Repository
```bash
git clone --recursive https://github.com/SURYAKNIGHT17/V_Streamer.git
cd V_Streamer
```

### 2. Linux (Ubuntu / Debian) Build & Setup

```bash
# Update and install system dependencies
sudo apt-get update && sudo apt-get install -y \
    build-essential cmake ninja-build pkg-config \
    libavcodec-dev libavformat-dev libavutil-dev libswscale-dev \
    libv4l-dev v4l2loopback-dkms \
    python3-dev python3-pip python3-venv

# Initialize virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure and compile with Ninja
cmake -B build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_CUDA=ON \
    -DENABLE_PYTHON_BINDINGS=ON

cmake --build build --config Release -j$(nproc)
```

### 3. Windows (MSVC + PowerShell) Build & Setup

```powershell
# In an elevated Developer PowerShell for VS 2022:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure CMake with MSVC Release flags
cmake -B build -G "Visual Studio 17 2022" -A x64 `
    -DCMAKE_BUILD_TYPE=Release `
    -DENABLE_CUDA=ON `
    -DENABLE_PYTHON_BINDINGS=ON

cmake --build build --config Release --parallel
```

### 4. Install Python Extension Module
```bash
pip install -e .
```

---

## Usage

### Option A: Python High-Level API

```python
import numpy as np
from vstreamer import StreamerConfig, VideoStreamer, CodecType, TransportProtocol

# 1. Configure the low-latency hardware pipeline
config = StreamerConfig(
    width=1920,
    height=1080,
    fps=60,
    bitrate_kbps=6000,
    codec=CodecType.H264_NVENC,
    protocol=TransportProtocol.WEBRTC,
    enable_virtual_cam=True,
    zero_copy=True
)

# 2. Instantiate and launch the engine
streamer = VideoStreamer(config)
streamer.start(endpoint="webrtc://0.0.0.0:8554/live")

try:
    print("[INFO] V_Streamer active. Streaming 1080p60 frame loop...")
    while streamer.is_running():
        # Allocate or acquire zero-copy frame buffer (RGBA / BGR)
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # Push frame into ring buffer (non-blocking, hardware-synced)
        streamer.push_frame(frame)
except KeyboardInterrupt:
    print("[INFO] Shutdown signal received.")
finally:
    streamer.stop()
```

### Option B: C++20 Native Pipeline

```cpp
#include <vstreamer/core/types.hpp>
#include <vstreamer/encoder/nvenc_encoder.hpp>
#include <vstreamer/transport/webrtc_node.hpp>
#include <iostream>

int main() {
    vstreamer::StreamConfig cfg{
        .width = 1920,
        .height = 1080,
        .framerate = 60,
        .bitrate = 6'000'000,
        .codec = vstreamer::Codec::H264_NVENC
    };

    auto encoder = std::make_unique<vstreamer::NvencEncoder>(cfg);
    encoder->initialize();

    auto transport = std::make_unique<vstreamer::WebRtcNode>("0.0.0.0", 8554);
    transport->start();

    std::cout << "[INFO] Native pipeline running at 1080p60.\n";

    // Main frame loop
    while (transport->is_connected()) {
        vstreamer::RawFrame frame = acquire_next_frame();
        vstreamer::EncodedPacket packet = encoder->encode(frame);
        transport->broadcast(std::move(packet));
    }

    encoder->shutdown();
    transport->stop();
    return 0;
}
```

---

## Performance Benchmarking

All performance validation tests were conducted using our automated harness ([`benchmarks/run_benchmarks.py`](benchmarks/run_benchmarks.py)). Raw telemetry data is archived in [`benchmarks/benchmarks.json`](benchmarks/benchmarks.json).

### Test Environment
* **Platform:** Ubuntu 22.04 LTS (Kernel 6.2.0-37-generic) / Windows 11 Pro 23H2
* **Processor:** AMD Ryzen 9 7900X (12 Cores, 24 Threads @ 4.7 GHz)
* **Graphics:** NVIDIA GeForce RTX 4080 (16 GB VRAM, Driver 550.54.14)
* **Memory:** 32 GB DDR5-6000 CL30

### 1. Frame Processing & Encode Latency
The table below documents average and 99th percentile frame encoding times across resolutions at 60 FPS:

| Resolution | Codec / Encoder | Avg Frame Encode Time | P99 Latency | Glass-to-Glass Latency | Zero-Copy Drop Rate |
|---|---|:---:|:---:|:---:|:---:|
| **1080p (1920x1080)** | NVENC H.264 (Low-Latency HQ) | **1.82 ms** | **2.65 ms** | **34.2 ms** | 0.00% |
| **1080p (1920x1080)** | Software libx264 (ultrafast) | 6.45 ms | 11.20 ms | 78.4 ms | 0.02% |
| **1440p (2560x1440)** | NVENC HEVC (Low-Latency HQ) | **2.94 ms** | **3.88 ms** | **42.1 ms** | 0.00% |
| **4K UHD (3840x2160)** | NVENC AV1 (CBR Low-Latency) | **4.15 ms** | **5.42 ms** | **58.7 ms** | 0.00% |

<div align="center">
  <img src="./assets/latency_chart.png" alt="Frame Processing, Encode, and Glass-to-Glass Latency by Codec" width="850"/>
</div>

### 2. Memory Consumption (Resident Set Size - RSS)
Memory footprint was recorded across continuous 60-minute stress runs:

| Test Mode | Baseline (Init) | Steady State (30m) | Peak RSS (60m) | Allocation Strategy |
|---|:---:|:---:|:---:|---|
| **1080p60 WebRTC Ingest** | 94.2 MB | 138.4 MB | **142.1 MB** | SPSC Lock-free Ring Buffer |
| **4K60 Transcode + VCam** | 162.8 MB | 248.5 MB | **268.0 MB** | CUDA Unified Pinned Memory |
| **Multi-Stream (4x 1080p)** | 210.4 MB | 385.2 MB | **412.6 MB** | Shared Memory IPC Pools |

<div align="center">
  <img src="./assets/memory_chart.png" alt="Resident Set Size (RSS) Memory Profile Over 60 Minutes" width="850"/>
</div>

> **Raw Telemetry Metrics:**  
> Detailed machine-readable JSON benchmarks with P50/P95/P99 latency, dropped frame counts, and GPU VRAM statistics are archived in [`benchmarks/benchmarks.json`](benchmarks/benchmarks.json). Re-run verification using [`python benchmarks/generate_charts.py`](benchmarks/generate_charts.py).

---

## Contributing

We welcome contributions from the community! To maintain performance and code quality:

1. **Fork & Branch:** Create a feature branch (`git checkout -b feature/cuda-pbr-pipeline`).
2. **Code Standards:** 
   - C++: Follow `clang-format` based on the Google C++ Style Guide with C++20 idioms.
   - Python: Follow PEP 8 and format with `ruff` and `black`.
3. **Performance Invariant:** Any PR introducing a $>5\%$ regression in P99 latency or heap allocations on the hot path will require optimization before merging.
4. **Submit PR:** Open a Pull Request referencing the related issue with benchmark logs attached.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
