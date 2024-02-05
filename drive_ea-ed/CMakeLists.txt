cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(drive_ea-ed_project C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(drive_ea-ed main.c)

pico_enable_stdio_usb(drive_ea-ed 1)
pico_enable_stdio_uart(drive_ea-ed 1)

# Inclua o suporte ao ADC
target_link_libraries(drive_ea-ed PRIVATE pico_stdlib hardware_adc hardware_pwm pico_multicore)

pico_add_extra_outputs(drive_ea-ed)
