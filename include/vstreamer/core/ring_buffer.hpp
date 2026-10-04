#pragma once

#include <atomic>
#include <vector>
#include <optional>
#include <cstddef>
#include "types.hpp"

namespace vstreamer {

/**
 * Lock-free Single-Producer Single-Consumer (SPSC) circular ring buffer.
 * Provides deterministic O(1) push and pop with zero heap allocation on the hot path.
 */
class LockFreeFrameRingBuffer {
public:
    explicit LockFreeFrameRingBuffer(size_t capacity = 8);
    ~LockFreeFrameRingBuffer() = default;

    // Non-copyable, non-movable for cache alignment safety
    LockFreeFrameRingBuffer(const LockFreeFrameRingBuffer&) = delete;
    LockFreeFrameRingBuffer& operator=(const LockFreeFrameRingBuffer&) = delete;

    bool try_push(RawFrame frame);
    std::optional<RawFrame> try_pop();

    [[nodiscard]] size_t size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    [[nodiscard]] size_t capacity() const noexcept { return capacity_; }

private:
    const size_t capacity_;
    std::vector<RawFrame> buffer_;
    alignas(64) std::atomic<size_t> head_{0};
    alignas(64) std::atomic<size_t> tail_{0};
};

} // namespace vstreamer
