// SPDX-License-Identifier: AGPL-3.0-only
#pragma once
#include "mha_algo_comm.hh"
#include "mha_signal.hh"
#include "mhapluginloader.h"
#include <portaudio.h>
#include <atomic>
#include <memory>
#include <string>

struct Settings {
    int input=-1, output=-1, mode=0;
    bool tone=false;
    double rate=48000, gain=0, cutoff=3000, ratio=2, peak=100;
};
class Processor {
    MHA_AC::algo_comm_class_t ac;
    PluginLoader::mhapluginloader_t chain{ac,"mhachain"};
    MHASignal::waveform_t wave{128,2};
    bool prepared=false;
public:
    explicit Processor(const Settings&);
    ~Processor();
    void render(const float*,float*,int,int);
};
class Engine {
    PaStream* stream=nullptr;
    std::unique_ptr<Processor> processor;
    Settings settings;
    int inputChannels=0,outputChannels=2;
    double phase=0;
    float currentVolume=0;
    static int callback(const void*,void*,unsigned long,const PaStreamCallbackTimeInfo*,PaStreamCallbackFlags,void*);
public:
    std::atomic<bool> audible{false};
    std::atomic<float> volume{0.1f}, inputPeak{0},outputPeak{0};
    std::atomic<unsigned> xruns{0},blocks{0};
    std::atomic<int> fault{0};
    Engine();
    ~Engine();
    void start(const Settings&);
    void stop();
    void refreshDevices();
    bool running() const;
    double latencyMs() const;
};
