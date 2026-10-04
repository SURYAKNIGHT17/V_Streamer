"""
V_Streamer 10-Minute Real Hardware Benchmark Harness
Executes an actual 600-second (10-minute) real-time video encoding stream on the local PC,
measuring exact frame encode latency (time.perf_counter), physical memory (RSS via psutil),
CPU utilization, and frame throughput.

Outputs:
  - benchmarks/benchmarks.json (Real measured telemetry database)
  - assets/memory_chart.png (Real plotted 10-minute RAM curve)
  - assets/latency_chart.png (Real plotted latency distribution)
"""

import os
import sys
import time
import json
import psutil
import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Paths
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
assets_dir = os.path.join(base_dir, "assets")
benchmarks_dir = os.path.join(base_dir, "benchmarks")
os.makedirs(assets_dir, exist_ok=True)
os.makedirs(benchmarks_dir, exist_ok=True)

# Settings
DURATION_SECONDS = 600  # 10 full minutes
TARGET_FPS = 30
FRAME_INTERVAL = 1.0 / TARGET_FPS
WIDTH = 1920
HEIGHT = 1080
TOTAL_FRAMES = DURATION_SECONDS * TARGET_FPS

print(f"====================================================================")
print(f"  V_Streamer 10-Minute Real Hardware Benchmark")
print(f"  Duration : {DURATION_SECONDS}s (10.0 minutes)")
print(f"  Target   : {WIDTH}x{HEIGHT} @ {TARGET_FPS} FPS ({TOTAL_FRAMES} frames)")
print(f"====================================================================\n")

# System specs
proc = psutil.Process(os.getpid())
initial_rss = proc.memory_info().rss / (1024 * 1024)
cpu_name = os.environ.get("PROCESSOR_IDENTIFIER", "x86_64 Processor")

# Initialize real VideoWriter
temp_video = os.path.join(benchmarks_dir, "temp_bench.mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(temp_video, fourcc, float(TARGET_FPS), (WIDTH, HEIGHT))

# Data storage
timeline_sec = []
timeline_rss = []
timeline_cpu = []
all_frame_latencies = []

start_time = time.perf_counter()
last_sample_time = start_time
frames_in_second = 0
latencies_in_second = []

print(f"[00:00] Starting real video encoding... Baseline RAM: {initial_rss:.1f} MB")

for frame_idx in range(TOTAL_FRAMES):
    loop_start = time.perf_counter()

    # 1. Generate real dynamic frame content with moving wave and timestamp
    t = frame_idx / TARGET_FPS
    # Synthetic frame with real dynamic gradient entropy
    grid_x = int((t * 200) % WIDTH)
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    # Dynamic color gradient
    frame[:, :, 0] = int((np.sin(t) + 1.0) * 80)
    frame[:, :, 1] = int((np.cos(t * 0.7) + 1.0) * 70)
    frame[:, :, 2] = int((np.sin(t * 1.3) + 1.0) * 100)
    # Draw moving cursor line & timestamp text
    cv2.line(frame, (grid_x, 0), (grid_x, HEIGHT), (255, 255, 255), 2)
    cv2.putText(frame, f"V_Streamer 10-Min Real Benchmark | Frame: {frame_idx} | Time: {t:.2f}s",
                (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

    # 2. Measure actual video encode time
    t_enc_start = time.perf_counter()
    writer.write(frame)
    t_enc_elapsed = (time.perf_counter() - t_enc_start) * 1000.0  # ms

    all_frame_latencies.append(t_enc_elapsed)
    latencies_in_second.append(t_enc_elapsed)
    frames_in_second += 1

    # 3. Sample system stats every 1 second
    now = time.perf_counter()
    if now - last_sample_time >= 1.0:
        elapsed = now - start_time
        current_rss = proc.memory_info().rss / (1024 * 1024)
        current_cpu = proc.cpu_percent()

        timeline_sec.append(round(elapsed, 1))
        timeline_rss.append(round(current_rss, 2))
        timeline_cpu.append(round(current_cpu, 1))

        avg_lat = np.mean(latencies_in_second) if latencies_in_second else 0.0
        fps_achieved = frames_in_second / (now - last_sample_time)

        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        pct = (elapsed / DURATION_SECONDS) * 100.0
        print(f"[{mins:02d}:{secs:02d} - {pct:4.1f}%] RAM: {current_rss:5.1f} MB | CPU: {current_cpu:4.1f}% | Encode: {avg_lat:5.2f} ms | FPS: {fps_achieved:4.1f}")

        # Reset 1-second counters
        last_sample_time = now
        frames_in_second = 0
        latencies_in_second = []

    # 4. Rate-limit to real-time 30 FPS pacing
    work_time = time.perf_counter() - loop_start
    sleep_time = FRAME_INTERVAL - work_time
    if sleep_time > 0:
        time.sleep(sleep_time)

# Cleanup video writer
writer.release()
actual_total_duration = time.perf_counter() - start_time
peak_rss = max(timeline_rss) if timeline_rss else initial_rss

print(f"\n====================================================================")
print(f"  Benchmark Completed in {actual_total_duration:.2f} seconds!")
print(f"  Total Frames Encoded : {len(all_frame_latencies)}")
print(f"  Peak RAM (RSS)       : {peak_rss:.1f} MB")
print(f"  Initial RAM (RSS)    : {initial_rss:.1f} MB")
print(f"  P50 Latency          : {np.percentile(all_frame_latencies, 50):.2f} ms")
print(f"  P95 Latency          : {np.percentile(all_frame_latencies, 95):.2f} ms")
print(f"  P99 Latency          : {np.percentile(all_frame_latencies, 99):.2f} ms")
print(f"====================================================================\n")

# Remove temp file
if os.path.exists(temp_video):
    try:
        os.remove(temp_video)
    except Exception:
        pass

# ------------------------------------------------------------------------------
# SAVE REAL DATA TO benchmarks/benchmarks.json
# ------------------------------------------------------------------------------
benchmark_data = {
    "schema_version": "1.0.0",
    "test_metadata": {
        "suite": "V_Streamer 10-Minute Real Hardware Benchmark",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "author": "SURYAKNIGHT17",
        "environment": {
            "os": f"Windows ({sys.platform})",
            "cpu": cpu_name,
            "opencv_version": cv2.__version__,
            "python_version": sys.version.split()[0],
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1)
        }
    },
    "results": {
        "duration_seconds": round(actual_total_duration, 1),
        "total_frames_encoded": len(all_frame_latencies),
        "achieved_fps": round(len(all_frame_latencies) / actual_total_duration, 2),
        "memory_metrics_mb": {
            "initial_rss": round(initial_rss, 1),
            "peak_rss": round(peak_rss, 1),
            "final_rss": round(timeline_rss[-1] if timeline_rss else peak_rss, 1)
        },
        "latency_metrics_ms": {
            "p50_frame_encode_time": round(float(np.percentile(all_frame_latencies, 50)), 2),
            "p90_frame_encode_time": round(float(np.percentile(all_frame_latencies, 90)), 2),
            "p95_frame_encode_time": round(float(np.percentile(all_frame_latencies, 95)), 2),
            "p99_frame_encode_time": round(float(np.percentile(all_frame_latencies, 99)), 2),
            "avg_frame_encode_time": round(float(np.mean(all_frame_latencies)), 2)
        }
    }
}

json_path = os.path.join(benchmarks_dir, "benchmarks.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(benchmark_data, f, indent=2)
print(f"[OK] Saved real benchmark data to {json_path}")

# ------------------------------------------------------------------------------
# PLOT REAL GRAPH 1: MEMORY PROFILE (10 MINUTES OF REAL DATA)
# ------------------------------------------------------------------------------
plt.style.use("dark_background")
bg_color = "#0f0f13"
panel_color = "#16161f"
grid_color = "#2a2a38"
text_color = "#e8e8f0"

fig, ax = plt.subplots(figsize=(10, 5), dpi=200, facecolor=bg_color)
ax.set_facecolor(panel_color)

mins_axis = [s / 60.0 for s in timeline_sec]
ax.plot(mins_axis, timeline_rss, color="#82aaff", linewidth=2.0, label="Real Measured RSS (MB)")

# Mark peak
max_idx = int(np.argmax(timeline_rss)) if timeline_rss else 0
max_x = mins_axis[max_idx]
max_y = timeline_rss[max_idx]
ax.annotate(f"Peak RAM: {max_y:.1f} MB (at {max_x:.1f}m)",
            xy=(max_x, max_y),
            xytext=(max(0.5, max_x - 2.5), max_y + 12),
            arrowprops=dict(arrowstyle="->", color="#ff5370", lw=1.5),
            color="#ff5370", fontweight="bold", fontsize=9.5)

ax.set_title("V_Streamer: Real 10-Minute Measured Memory Profile (RSS)", fontsize=13, fontweight="bold", pad=15, color=text_color)
ax.set_xlabel("Elapsed Time (Minutes)", fontsize=10, color="#a0a0b8", labelpad=8)
ax.set_ylabel("Resident Memory (MB)", fontsize=10, color="#a0a0b8", labelpad=8)
ax.set_xlim(0, max(mins_axis) + 0.2 if mins_axis else 10)
ax.set_ylim(min(timeline_rss) - 10, max(timeline_rss) + 25)
ax.grid(True, linestyle="--", alpha=0.35, color=grid_color)
ax.legend(loc="lower right", framealpha=0.85, facecolor="#1f1f2b", edgecolor=grid_color, fontsize=9)

plt.tight_layout()
mem_chart_path = os.path.join(assets_dir, "memory_chart.png")
fig.savefig(mem_chart_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
plt.close(fig)
print(f"[OK] Generated real graph: {mem_chart_path}")

# ------------------------------------------------------------------------------
# PLOT REAL GRAPH 2: LATENCY DISTRIBUTION
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5), dpi=200, facecolor=bg_color)
ax.set_facecolor(panel_color)

categories = ["P50 (Median)", "P90 Latency", "P95 Latency", "P99 Latency", "Avg Encode"]
vals = [
    float(np.percentile(all_frame_latencies, 50)),
    float(np.percentile(all_frame_latencies, 90)),
    float(np.percentile(all_frame_latencies, 95)),
    float(np.percentile(all_frame_latencies, 99)),
    float(np.mean(all_frame_latencies))
]
colors = ["#80cbc4", "#82aaff", "#c792ea", "#ff5370", "#ffcb6b"]

bars = ax.bar(categories, vals, color=colors, width=0.45, edgecolor="#2a2a38")

for bar in bars:
    height = bar.get_height()
    ax.annotate(f"{height:.2f} ms",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center", va="bottom", fontsize=9, color="#e8e8f0", fontweight="600")

ax.set_title("V_Streamer: Real Measured 1080p Frame Encode Latency Distribution", fontsize=13, fontweight="bold", pad=15, color=text_color)
ax.set_ylabel("Frame Time (Milliseconds - Lower is Better)", fontsize=10, color="#a0a0b8", labelpad=8)
ax.set_ylim(0, max(vals) * 1.3)
ax.grid(True, linestyle="--", alpha=0.35, color=grid_color, axis="y")

plt.tight_layout()
lat_chart_path = os.path.join(assets_dir, "latency_chart.png")
fig.savefig(lat_chart_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
plt.close(fig)
print(f"[OK] Generated real graph: {lat_chart_path}")

print("\nAll real benchmark artifacts generated successfully!")
