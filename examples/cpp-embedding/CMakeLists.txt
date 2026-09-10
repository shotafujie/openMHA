cmake_minimum_required(VERSION 3.20)
project(openmha_embedding LANGUAGES CXX)

set(OPENMHA_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../.local" CACHE PATH
    "Prefix containing an installed openMHA")
find_path(OPENMHA_INCLUDE_DIR mha_toolbox.h
    PATHS "${OPENMHA_ROOT}/include/openmha" NO_DEFAULT_PATH REQUIRED)
find_library(OPENMHA_LIBRARY NAMES openmha
    PATHS "${OPENMHA_ROOT}/lib" NO_DEFAULT_PATH REQUIRED)

add_executable(openmha_embedding main.cpp)
target_compile_features(openmha_embedding PRIVATE cxx_std_17)
target_compile_options(openmha_embedding PRIVATE -Wall -Wextra -Wpedantic)
target_include_directories(openmha_embedding SYSTEM PRIVATE "${OPENMHA_INCLUDE_DIR}")
target_link_libraries(openmha_embedding PRIVATE "${OPENMHA_LIBRARY}")
set_target_properties(openmha_embedding PROPERTIES
    BUILD_RPATH "${OPENMHA_ROOT}/lib")

enable_testing()
add_test(NAME embedded_gain COMMAND openmha_embedding)
set_tests_properties(embedded_gain PROPERTIES
    ENVIRONMENT "MHA_LIBRARY_PATH=${OPENMHA_ROOT}/lib")

# End-to-end check of the existing CLI + MHAIOFile + mhachain + gain example.
find_package(PkgConfig REQUIRED)
pkg_check_modules(SNDFILE REQUIRED IMPORTED_TARGET sndfile)
add_executable(verify_gain_file verify_gain_file.cpp)
target_compile_features(verify_gain_file PRIVATE cxx_std_17)
target_link_libraries(verify_gain_file PRIVATE PkgConfig::SNDFILE)
find_program(OPENMHA_EXECUTABLE mha PATHS "${OPENMHA_ROOT}/bin"
    NO_DEFAULT_PATH REQUIRED)
add_executable(process_file process_file.cpp)
target_compile_features(process_file PRIVATE cxx_std_17)
target_compile_options(process_file PRIVATE -Wall -Wextra -Wpedantic)
target_include_directories(process_file SYSTEM PRIVATE "${OPENMHA_INCLUDE_DIR}")
target_link_libraries(process_file PRIVATE "${OPENMHA_LIBRARY}" PkgConfig::SNDFILE)
set_target_properties(process_file PROPERTIES BUILD_RPATH "${OPENMHA_ROOT}/lib")
add_test(NAME render_gain_file COMMAND "${OPENMHA_EXECUTABLE}"
    "?read:gain.cfg" "io.out=${CMAKE_CURRENT_BINARY_DIR}/gain-output.wav"
    "cmd=start" "cmd=quit")
set_tests_properties(render_gain_file PROPERTIES
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../00-gain"
    ENVIRONMENT "MHA_LIBRARY_PATH=${OPENMHA_ROOT}/lib"
    FIXTURES_SETUP gain_file TIMEOUT 30)
add_test(NAME verify_gain_file COMMAND verify_gain_file
    "${CMAKE_CURRENT_SOURCE_DIR}/../00-gain/1speaker_diffNoise_2ch.wav"
    "${CMAKE_CURRENT_BINARY_DIR}/gain-output.wav")
set_tests_properties(verify_gain_file PROPERTIES FIXTURES_REQUIRED gain_file)

# These exact paths are disposable test outputs under this build directory.
add_test(NAME clear_chain_outputs COMMAND "${CMAKE_COMMAND}" -E rm -f
    "${CMAKE_CURRENT_BINARY_DIR}/gain-chain.wav"
    "${CMAKE_CURRENT_BINARY_DIR}/lowpass-chain.wav")
set_tests_properties(clear_chain_outputs PROPERTIES FIXTURES_SETUP chain_output_paths)
foreach(chain IN ITEMS gain lowpass)
    add_test(NAME render_${chain}_chain COMMAND process_file
        "${CMAKE_CURRENT_SOURCE_DIR}/../00-gain/1speaker_diffNoise_2ch.wav"
        "${CMAKE_CURRENT_BINARY_DIR}/${chain}-chain.wav"
        "${CMAKE_CURRENT_SOURCE_DIR}/${chain}-chain.cfg")
    set_tests_properties(render_${chain}_chain PROPERTIES
        ENVIRONMENT "MHA_LIBRARY_PATH=${OPENMHA_ROOT}/lib" TIMEOUT 30
        FIXTURES_REQUIRED chain_output_paths FIXTURES_SETUP ${chain}_chain)
endforeach()
add_test(NAME verify_gain_chain COMMAND verify_gain_file
    "${CMAKE_CURRENT_SOURCE_DIR}/../00-gain/1speaker_diffNoise_2ch.wav"
    "${CMAKE_CURRENT_BINARY_DIR}/gain-chain.wav")
set_tests_properties(verify_gain_chain PROPERTIES FIXTURES_REQUIRED gain_chain)
add_test(NAME verify_lowpass_chain COMMAND verify_gain_file
    "${CMAKE_CURRENT_SOURCE_DIR}/../00-gain/1speaker_diffNoise_2ch.wav"
    "${CMAKE_CURRENT_BINARY_DIR}/lowpass-chain.wav" --lowpass)
set_tests_properties(verify_lowpass_chain PROPERTIES FIXTURES_REQUIRED lowpass_chain)
add_test(NAME reject_existing_output COMMAND process_file
    "${CMAKE_CURRENT_SOURCE_DIR}/../00-gain/1speaker_diffNoise_2ch.wav"
    "${CMAKE_CURRENT_BINARY_DIR}/gain-chain.wav"
    "${CMAKE_CURRENT_SOURCE_DIR}/gain-chain.cfg")
set_tests_properties(reject_existing_output PROPERTIES
    ENVIRONMENT "MHA_LIBRARY_PATH=${OPENMHA_ROOT}/lib"
    FIXTURES_REQUIRED gain_chain WILL_FAIL TRUE)
