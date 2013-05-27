
cmake_minimum_required(VERSION 2.8)

file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

set( CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake ${CMAKE_CURRENT_SOURCE_DIR})

set(CMAKE_INCLUDE_CURRENT_DIR ON) 

###################
# PYTHON / CYTHON #
###################

# Python is used throughout, might aswell include the headers here
#find_package(PythonModules)
#include_directories( ${NUMPY_INCLUDE_DIR} )

# Include the CMake script UseCython.cmake. This defines add_cython_module().
# Instruction for use can be found at the top of cmake/UseCython.cmake.
include(UseCython)

# Set some Cython options
set(CYTHON_ANNOTATE ON)
set(CYTHON_FLAGS "--verbose" "-X profile=False,cdivision=True,wraparound=False,boundscheck=False")
# set(CYTHON_FLAGS "--verbose" "-X profile=False,cdivision=False,wraparound=True,boundscheck=True")
#set(CYTHON_FLAGS "-X profile=False,cdivision=True,wraparound=False,boundscheck=False")


cython_add_module(macro macro.py)
cython_add_module(gui_module gui_module.pyx)

add_executable(gui gui.cpp)

target_link_libraries(gui gui_module)

#install(TARGETS gpumat
#        DESTINATION ${CMAKE_SOURCE_DIR}/lib )