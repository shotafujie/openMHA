// SPDX-License-Identifier: AGPL-3.0-only
// A standalone C++ host: no MATLAB, TCP server, or audio device required.
#include "mha_algo_comm.hh"
#include "mha_signal.hh"
#include "mhapluginloader.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <stdexcept>

class GainProcessor {
    // Declaration order matters: the plugin must be destroyed before AC space.
    MHA_AC::algo_comm_class_t ac_;
    PluginLoader::mhapluginloader_t plugin_{ac_, "gain"};
    bool prepared_ = false;

public:
    explicit GainProcessor(unsigned frames, float sample_rate) {
        mhaconfig_t format{};
        format.channels = 2;
        format.domain = MHA_WAVEFORM;
        format.fragsize = frames;
        format.srate = sample_rate;
        plugin_.parse("gains=[0 0]");
        plugin_.prepare(format);
        prepared_ = true;
        ac_.set_prepared(true);
    }

    GainProcessor(const GainProcessor&) = delete;
    GainProcessor& operator=(const GainProcessor&) = delete;

    ~GainProcessor() {
        if (prepared_) {
            ac_.set_prepared(false);
            try { plugin_.release(); }
            catch (...) { /* Destructors must not throw during unwinding. */ }
        }
    }

    // Configure between blocks on this demo's single thread.
    void set_gains(const std::string& gains) {
        plugin_.parse("gains=" + gains);
    }

    mha_wave_t* process(mha_wave_t& input) {
        mha_wave_t* output = nullptr;
        plugin_.process(&input, &output);
        if (!output) throw std::runtime_error("Plugin returned no output");
        return output;  // Borrowed buffer; gain modifies input in place.
    }

    void release() {
        ac_.set_prepared(false);
        plugin_.release();
        prepared_ = false;
    }
};

int main() {
    try {
        constexpr unsigned frames = 128;
        constexpr float sample_rate = 48000;
        constexpr double pi = 3.14159265358979323846;
        GainProcessor processor(frames, sample_rate);
        MHASignal::waveform_t input(frames, 2);
        // Distinct channel gains catch channel-order and dB conversion errors.
        const std::array<std::array<double, 2>, 3> cases{{
            {{0, 0}}, {{-6, 6}}, {{3, -12}}
        }};
        const std::array<const char*, 3> settings{
            "[0 0]", "[-6 6]", "[3 -12]"
        };
        double max_error = 0;
        unsigned blocks = 0;
        for (unsigned test = 0; test < cases.size(); ++test) {
            processor.set_gains(settings[test]);
            for (unsigned block = 0; block < 8; ++block) {
                std::array<std::array<float, 2>, frames> original{};
                for (unsigned frame = 0; frame < frames; ++frame) {
                    for (unsigned channel = 0; channel < 2; ++channel) {
                        const double phase = 2 * pi * (channel ? 1700 : 1000)
                            * (blocks * frames + frame) / sample_rate;
                        const float sample = 0.1f * std::sin(phase);
                        original[frame][channel] = sample;
                        input.value(frame, channel) = sample;
                    }
                }
                mha_wave_t* output = processor.process(input);
                if (output->num_frames != frames || output->num_channels != 2)
                    throw std::runtime_error("Unexpected output dimensions");
                for (unsigned frame = 0; frame < frames; ++frame) {
                    for (unsigned channel = 0; channel < 2; ++channel) {
                        const double expected = original[frame][channel]
                            * std::pow(10.0, cases[test][channel] / 20.0);
                        const double actual = value(output, frame, channel);
                        if (!std::isfinite(actual))
                            throw std::runtime_error("Non-finite output");
                        max_error = std::max(max_error, std::abs(actual - expected));
                    }
                }
                ++blocks;
            }
        }
        // Invalid settings must be rejected instead of silently accepted.
        bool rejected = false;
        try { processor.set_gains("[100 100]"); }
        catch (const std::exception&) { rejected = true; }
        if (!rejected) throw std::runtime_error("Out-of-range gain was accepted");
        processor.release();
        if (max_error > 1e-6)
            throw std::runtime_error("Gain output differs from reference");
        std::cout << "PASS: " << blocks << " stereo blocks at " << sample_rate
                  << " Hz; 3 gain settings; max absolute error=" << max_error
                  << "; invalid gain rejected\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 1;
    }
}
