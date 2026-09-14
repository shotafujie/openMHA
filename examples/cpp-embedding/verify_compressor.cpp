// SPDX-License-Identifier: AGPL-3.0-only
#include "mha_algo_comm.hh"
#include "mha_signal.hh"
#include "mhapluginloader.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <vector>

namespace {
constexpr double input_peak[2] = {100, 110};
constexpr double output_peak[2] = {100, 105};
void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
double amplitude(double level, double peak) { return std::pow(10., (level-peak)/20.); }
double level(double sample, double peak) { return 20*std::log10(std::abs(sample))+peak; }

struct Host {
    MHA_AC::algo_comm_class_t ac;
    PluginLoader::mhapluginloader_t chain{ac, "mhachain"};
    bool prepared = false;
    Host(const char* config, unsigned frames, bool instantaneous) {
        chain.parse(std::string("?read:")+config);
        if (instantaneous) {
            chain.parse("calibrated.dc_simple.tau_attack=[0]");
            chain.parse("calibrated.dc_simple.tau_decay=[0]");
        }
        mhaconfig_t format{};
        format.channels=2; format.domain=MHA_WAVEFORM;
        format.fragsize=frames; format.srate=48000;
        chain.prepare(format);
        prepared=true;
        ac.set_prepared(true);
    }
    ~Host() {
        ac.set_prepared(false);
        if (prepared) { try { chain.release(); } catch (...) {} }
    }
    mha_wave_t* process(mha_wave_t& input) {
        mha_wave_t* output=nullptr;
        chain.process(&input, &output);
        require(output && output->num_channels==2 && output->num_frames==input.num_frames,
                "Unexpected compressor dimensions");
        return output;
    }
    void finish() { ac.set_prepared(false); chain.release(); prepared=false; }
};

void static_checks(const char* config) {
    Host host(config, 128, true);
    MHASignal::waveform_t input(128,2);
    // Independently specified points on expansion, 2:1 compression and limiting.
    const std::array<std::array<double,2>,9> points{{
        {{10,0}}, {{20,20}}, {{30,40}}, {{40,45}}, {{50,50}},
        {{65,57.5}}, {{80,65}}, {{90,70}}, {{95,70}}
    }};
    double worst=0;
    for (const auto& point:points) {
        for(unsigned f=0;f<128;++f)
            for(unsigned ch=0;ch<2;++ch)
                input.value(f,ch)=(f%2 ? -1 : 1)*amplitude(point[0],input_peak[ch]);
        const auto* output=host.process(input);
        for(unsigned f=0;f<128;++f)
            for(unsigned ch=0;ch<2;++ch) {
                const double actual=value(output,f,ch);
                require(std::isfinite(actual) && actual*(f%2 ? -1 : 1)>0,
                        "Non-finite output or polarity changed");
                worst=std::max(worst,std::abs(level(actual,output_peak[ch])-point[1]));
            }
    }
    require(worst<0.001,"Static input/output curve differs by more than 0.001 dB");
    // A stricter maxgain must cap the +10 dB gain at the expansion knee.
    host.chain.parse("calibrated.dc_simple.maxgain=[3]");
    for(unsigned f=0;f<128;++f) for(unsigned ch=0;ch<2;++ch)
        input.value(f,ch)=amplitude(30,input_peak[ch]);
    const auto* capped=host.process(input);
    for(unsigned ch=0;ch<2;++ch)
        require(std::abs(level(value(capped,127,ch),output_peak[ch])-33)<0.001,
                "maxgain or live parameter update failed");

    // Bypass only compression: calibration remains active (right channel +5 dB).
    host.chain.parse("calibrated.dc_simple.bypass=yes");
    for(unsigned f=0;f<128;++f) for(unsigned ch=0;ch<2;++ch) input.value(f,ch)=0.1f;
    const auto* bypass=host.process(input);
    for(unsigned ch=0;ch<2;++ch)
        require(std::abs(value(bypass,127,ch)-0.1*amplitude(input_peak[ch],output_peak[ch]))<1e-6,
                "Calibration passthrough failed");
    host.chain.parse("calibrated.dc_simple.bypass=no");
    for(unsigned f=0;f<128;++f) for(unsigned ch=0;ch<2;++ch) input.value(f,ch)=0;
    const auto* silence=host.process(input);
    for(unsigned f=0;f<128;++f) for(unsigned ch=0;ch<2;++ch)
        require(value(silence,f,ch)==0,"Silence produced nonzero or non-finite samples");
    host.finish();
    std::cout<<"PASS static: 9 SPL points, stereo calibration, polarity, maxgain, bypass, silence; max dB error="<<worst<<'\n';
}

std::vector<float> dynamic_response(const char* config,unsigned frames) {
    Host host(config,frames,false);
    MHASignal::waveform_t input(frames,2);
    constexpr unsigned total=144000, up=48013, down=96029;
    std::vector<float> result(total*2);
    for(unsigned offset=0;offset<total;offset+=frames) {
        for(unsigned f=0;f<frames;++f) {
            const auto n=offset+f;
            const double spl=n<up ? 40 : (n<down ? 80 : 40);
            for(unsigned ch=0;ch<2;++ch)
                input.value(f,ch)=(n%2 ? -1 : 1)*amplitude(spl,input_peak[ch]);
        }
        const auto* output=host.process(input);
        for(unsigned f=0;f<std::min(frames,total-offset);++f)
            for(unsigned ch=0;ch<2;++ch) {
                const float sample=value(output,f,ch);
                require(std::isfinite(sample),"Dynamic response produced non-finite output");
                result[(offset+f)*2+ch]=sample;
            }
    }
    for(unsigned ch=0;ch<2;++ch) {
        const auto at=[&](unsigned n){ return level(result[n*2+ch],output_peak[ch]); };
        require(std::abs(at(up-1)-45)<0.01 && std::abs(at(down-1)-65)<0.01 &&
                std::abs(at(total-1)-45)<0.01,"Dynamic response did not settle");
        require(at(up)>at(down-1)+10,"Attack smoothing was not observable");
        require(at(down)<at(total-1)-10,"Decay smoothing was not observable");
        for(unsigned n=up+1;n<down;++n)
            require(at(n)<=at(n-1)+0.001,"Attack gain did not decrease monotonically");
        for(unsigned n=down+1;n<total;++n)
            require(at(n)>=at(n-1)-0.001,"Decay gain did not recover monotonically");
    }
    host.finish();
    return result;
}
}

int main(int argc,char** argv) {
    try {
        require(argc==2,"Usage: verify_compressor compressor-chain.cfg");
        static_checks(argv[1]);
        const auto a=dynamic_response(argv[1],64);
        const auto b=dynamic_response(argv[1],128);
        double worst=0;
        for(size_t i=0;i<a.size();++i) worst=std::max(worst,std::abs(double(a[i])-b[i]));
        require(worst<1e-7,"Response depends on block size");
        std::cout<<"PASS dynamic: attack/decay, settling, off-boundary steps; 64 vs 128 frames max error="<<worst<<'\n';
        return 0;
    } catch(const std::exception& e) { std::cerr<<"FAIL: "<<e.what()<<'\n'; return 1; }
}
