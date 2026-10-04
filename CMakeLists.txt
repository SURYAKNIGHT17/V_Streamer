cmake_minimum_required(VERSION 3.22)
project(V_Streamer VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Build options
option(ENABLE_CUDA "Enable NVIDIA CUDA & NVENC hardware acceleration" ON)
option(ENABLE_PYTHON_BINDINGS "Build Python C++ bindings via pybind11" ON)
option(BUILD_TESTS "Build benchmark and verification tests" ON)

# Optimization Flags
if(MSVC)
    add_compile_options(/W4 /O2 /permissive- /Zc:__cplusplus)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -O3 -march=native)
endif()

# Include directories
include_directories(include)

# Source files
set(CORE_SOURCES
    src/core/ring_buffer.cpp
)

add_library(vstreamer_core STATIC ${CORE_SOURCES})
target_include_directories(vstreamer_core PUBLIC include)

# Python Bindings via pybind11
if(ENABLE_PYTHON_BINDINGS)
    find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
    find_package(pybind11 CONFIG QUIET)
    if(NOT pybind11_FOUND)
        # Fallback to python pip pybind11 cmake directory
        execute_process(
            COMMAND "${Python3_EXECUTABLE}" -m pybind11 --cmakedir
            OUTPUT_VARIABLE pybind11_DIR
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        find_package(pybind11 REQUIRED CONFIG PATHS ${pybind11_DIR})
    endif()

    pybind11_add_module(_vstreamer python/bindings/py_vstreamer.cpp)
    target_link_libraries(_vstreamer PRIVATE vstreamer_core)
endif()
