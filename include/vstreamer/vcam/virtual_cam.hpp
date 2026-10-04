#pragma once

#include <string>
#include <cstdint>
#include <memory>
#include "../core/types.hpp"

namespace vstreamer {

/**
 * Cross-platform virtual camera device driver interface.
 * Implements DirectShow virtual source on Windows and v4l2loopback on Linux.
 */
class VirtualCamera {
public:
    VirtualCamera(uint32_t width, uint32_t height, uint32_t fps, const std::string& device_name = "V_Streamer Virtual Camera");
    ~VirtualCamera();

    bool open();
    bool send_frame(const RawFrame& frame);
    void close();

    [[nodiscard]] bool is_active() const noexcept { return is_active_; }
    [[nodiscard]] const std::string& device_name() const noexcept { return device_name_; }

private:
    uint32_t width_;
    uint32_t height_;
    uint32_t fps_;
    std::string device_name_;
    bool is_active_{false};
};

} // namespace vstreamer
