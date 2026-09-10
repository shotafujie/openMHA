// SPDX-License-Identifier: AGPL-3.0-only
// Verify every output sample of examples/00-gain against its configured gains.
#include <sndfile.h>
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

int main(int argc, char** argv) {
    try {
        const bool lowpass = argc == 4 && std::string(argv[3]) == "--lowpass";
        if (argc != 3 && !lowpass)
            throw std::runtime_error("Usage: verify_gain_file input output [--lowpass]");
        SF_INFO in_info{}, out_info{};
        using SoundFile = std::unique_ptr<SNDFILE, decltype(&sf_close)>;
        SoundFile input(sf_open(argv[1], SFM_READ, &in_info), sf_close);
        SoundFile output(sf_open(argv[2], SFM_READ, &out_info), sf_close);
        if (!input || !output) throw std::runtime_error("Could not open WAV files");
        if (in_info.channels != 2 || out_info.channels != 2 ||
            in_info.samplerate != out_info.samplerate ||
            in_info.frames != out_info.frames || in_info.frames <= 0)
            throw std::runtime_error("WAV dimensions differ or input is empty");
        const std::array<double, 2> gains{std::pow(10., -10./20.), std::pow(10., 10./20.)};
        std::array<double, 2048> in{}, out{};
        sf_count_t total = 0;
        double max_error = 0;
        std::array<double, 2> previous{};
        for (;;) {
            const auto count = sf_readf_double(input.get(), in.data(), 1024);
            const auto written = sf_readf_double(output.get(), out.data(), 1024);
            if (count != written) throw std::runtime_error("WAV read lengths differ");
            if (!count) break;
            for (sf_count_t i = 0; i < count * 2; ++i) {
                if (!std::isfinite(in[i]) || !std::isfinite(out[i]))
                    throw std::runtime_error("Non-finite sample");
                const auto channel = i % 2;
                const double expected = lowpass
                    ? 0.5 * (in[i] + previous[channel]) * std::pow(10., -6./20.)
                    : in[i] * gains[channel];
                previous[channel] = in[i];
                max_error = std::max(max_error, std::abs(out[i] - expected));
            }
            total += count;
        }
        if (sf_error(input.get()) || sf_error(output.get()) || total != in_info.frames)
            throw std::runtime_error("Incomplete WAV read");
        if (max_error > 1e-6) throw std::runtime_error("WAV gain differs from reference");
        std::cout << "PASS: " << total << " stereo frames; "
                  << (lowpass ? "two-tap lowpass, -6 dB; " : "gains=[-10 10] dB; ")
                  << "max absolute error=" << max_error << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 1;
    }
}
