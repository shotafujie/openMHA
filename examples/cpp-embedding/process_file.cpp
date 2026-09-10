// SPDX-License-Identifier: AGPL-3.0-only
// POSIX offline host for frame-preserving waveform processing chains.
#include "mha_algo_comm.hh"
#include "mha_signal.hh"
#include "mhapluginloader.h"
#include <sndfile.h>
#include <fcntl.h>
#include <unistd.h>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <vector>

class Chain {
    MHA_AC::algo_comm_class_t ac_;
    PluginLoader::mhapluginloader_t plugin_{ac_, "mhachain"};
    bool prepared_ = false;
public:
    Chain(const char* configuration, mhaconfig_t format) {
        plugin_.parse(std::string("?read:") + configuration);
        const auto input = format;
        plugin_.prepare(format);
        prepared_ = true;
        if (format.domain != MHA_WAVEFORM || format.fragsize != input.fragsize ||
            format.channels != input.channels || format.srate != input.srate) {
            plugin_.release();
            prepared_ = false;
            throw std::runtime_error("This host requires unchanged waveform dimensions and rate");
        }
        ac_.set_prepared(true);
    }
    Chain(const Chain&) = delete;
    Chain& operator=(const Chain&) = delete;
    ~Chain() {
        ac_.set_prepared(false);
        if (prepared_) {
            try { plugin_.release(); } catch (...) {}
        }
    }
    mha_wave_t* process(mha_wave_t& input) {
        mha_wave_t* output = nullptr;
        plugin_.process(&input, &output);
        if (!output || output->num_channels != input.num_channels ||
            output->num_frames != input.num_frames)
            throw std::runtime_error("Unexpected output dimensions");
        return output;
    }
    void release() {
        ac_.set_prepared(false);
        plugin_.release();
        prepared_ = false;
    }
};

int main(int argc, char** argv) {
    try {
        if (argc != 4)
            throw std::runtime_error("Usage: process_file INPUT.wav NEW_OUTPUT.wav CHAIN.cfg");
        SF_INFO info{};
        using SoundFile = std::unique_ptr<SNDFILE, decltype(&sf_close)>;
        SoundFile input(sf_open(argv[1], SFM_READ, &info), sf_close);
        if (!input) throw std::runtime_error(sf_strerror(nullptr));
        if (info.channels < 1 || info.channels > 64 || info.samplerate <= 0 || info.frames <= 0)
            throw std::runtime_error("Expected non-empty audio with 1 to 64 channels");

        constexpr unsigned frames = 128;
        mhaconfig_t format{};
        format.channels = info.channels;
        format.domain = MHA_WAVEFORM;
        format.fragsize = frames;
        format.srate = info.samplerate;
        Chain chain(argv[3], format);
        MHASignal::waveform_t block(frames, info.channels);
        std::vector<float> samples(frames * info.channels);
        SF_INFO output_info = info;
        output_info.format = SF_FORMAT_WAV | SF_FORMAT_FLOAT;
        // Exclusive creation also prevents overwriting the input through aliases.
        const int descriptor = open(argv[2], O_CREAT | O_EXCL | O_RDWR, 0600);
        if (descriptor < 0)
            throw std::runtime_error("Cannot create output; choose a new writable path");
        SoundFile output(sf_open_fd(descriptor, SFM_WRITE, &output_info, SF_TRUE), sf_close);
        if (!output) {
            close(descriptor);
            throw std::runtime_error("Cannot initialize output WAV");
        }
        sf_count_t total = 0;
        double peak = 0;
        for (;;) {
            std::fill(samples.begin(), samples.end(), 0.f);
            const auto count = sf_readf_float(input.get(), samples.data(), frames);
            if (!count) break;
            for (unsigned f = 0; f < frames; ++f)
                for (int ch = 0; ch < info.channels; ++ch) {
                    const float sample = samples[f * info.channels + ch];
                    if (!std::isfinite(sample)) throw std::runtime_error("Non-finite input");
                    block.value(f, ch) = sample;
                }
            const mha_wave_t* processed = chain.process(block);
            for (sf_count_t f = 0; f < count; ++f)
                for (int ch = 0; ch < info.channels; ++ch) {
                    const float sample = value(processed, f, ch);
                    if (!std::isfinite(sample)) throw std::runtime_error("Non-finite output");
                    peak = std::max(peak, static_cast<double>(std::abs(sample)));
                    samples[f * info.channels + ch] = sample;
                }
            if (sf_writef_float(output.get(), samples.data(), count) != count)
                throw std::runtime_error("Incomplete output write");
            total += count;
        }
        if (sf_error(input.get()) || total != info.frames)
            throw std::runtime_error("Incomplete input read");
        chain.release();
        if (sf_close(output.release())) throw std::runtime_error("Failed to finalize WAV");
        std::cout << "Processed " << total << " frames, " << info.channels
                  << " channels at " << info.samplerate << " Hz; peak=" << peak << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what()
                  << "\nAn output created during a failed run may be incomplete.\n";
        return 1;
    }
}
