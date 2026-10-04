#include "vstreamer/core/ring_buffer.hpp"

namespace vstreamer {

LockFreeFrameRingBuffer::LockFreeFrameRingBuffer(size_t capacity)
    : capacity_(capacity + 1), buffer_(capacity + 1) {}

bool LockFreeFrameRingBuffer::try_push(RawFrame frame) {
    const size_t current_head = head_.load(std::memory_order_relaxed);
    const size_t next_head = (current_head + 1) % capacity_;

    if (next_head == tail_.load(std::memory_order_acquire)) {
        // Buffer is full; drop or backpressure
        return false;
    }

    buffer_[current_head] = std::move(frame);
    head_.store(next_head, std::memory_order_release);
    return true;
}

std::optional<RawFrame> LockFreeFrameRingBuffer::try_pop() {
    const size_t current_tail = tail_.load(std::memory_order_relaxed);

    if (current_tail == head_.load(std::memory_order_acquire)) {
        // Buffer is empty
        return std::nullopt;
    }

    RawFrame frame = std::move(buffer_[current_tail]);
    tail_.store((current_tail + 1) % capacity_, std::memory_order_release);
    return frame;
}

size_t LockFreeFrameRingBuffer::size() const noexcept {
    const size_t head = head_.load(std::memory_order_relaxed);
    const size_t tail = tail_.load(std::memory_order_relaxed);
    if (head >= tail) {
        return head - tail;
    }
    return capacity_ + head - tail;
}

bool LockFreeFrameRingBuffer::empty() const noexcept {
    return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
}

} // namespace vstreamer
