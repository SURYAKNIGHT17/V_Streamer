#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace vstreamer {

enum class PixelFormat {
    RGBA = 0,
    BGRA,
    RGB24,
    BGR24,
    NV12,
    YUV420P
};

enum class Codec {
    H264_NVENC = 0,
    HEVC_NVENC,
    AV1_NVENC,
    H264_QSV,
    LIBX264
};

enum class Protocol {
    WEBRTC = 0,
    SRT,
    RTMP,
    SHARED_MEMORY
};

struct StreamConfig {
    uint32_t width{1920};
    uint32_t height{1080};
    uint32_t framerate{60};
    uint32_t bitrate{6'000'000};
    Codec codec{Codec::H264_NVENC};
    PixelFormat input_format{PixelFormat::BGRA};
    bool zero_copy{true};
    bool enable_virtual_cam{true};
};

struct RawFrame {
    uint32_t width{0};
    uint32_t height{0};
    PixelFormat format{PixelFormat::BGRA};
    uint64_t timestamp_us{0};
    std::vector<uint8_t> data;
};

struct EncodedPacket {
    uint64_t dts_us{0};
    uint64_t pts_us{0};
    bool is_keyframe{false};
    std::vector<uint8_t> payload;
};

} // namespace vstreamer
