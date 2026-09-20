// SPDX-License-Identifier: AGPL-3.0-only
#include "engine.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
static_assert(std::atomic<float>::is_always_lock_free);
static_assert(std::atomic<unsigned>::is_always_lock_free);
static void check(PaError e) { if(e<0) throw std::runtime_error(Pa_GetErrorText(e)); }
Processor::Processor(const Settings& s) {
    if(s.mode<0||s.mode>2||!std::isfinite(s.rate)||s.rate<32000||s.rate>96000||
       !std::isfinite(s.gain)||s.gain < -16||s.gain>16||!std::isfinite(s.cutoff)||
       s.cutoff<=0||s.cutoff>=s.rate/2||!std::isfinite(s.ratio)||s.ratio<1||s.ratio>10||
       !std::isfinite(s.peak)||s.peak<80||s.peak>120)
        throw std::runtime_error("Invalid audio processing settings");
    const auto set=[&](const std::string& key,double v){chain.parse(key+"="+std::to_string(v));};
    if(s.mode==0) {
        chain.parse("algos=[gain]"); set("gain.gains",s.gain);
    } else if(s.mode==1) {
        chain.parse("algos=[gain iirfilter]");set("gain.gains",s.gain);
        const double a=std::exp(-2*3.141592653589793*s.cutoff/s.rate);
        chain.parse("iirfilter.A=[1 "+std::to_string(-a)+"]");
        chain.parse("iirfilter.B=["+std::to_string(1-a)+"]");
    } else {
        chain.parse("algos=[transducers:c gain]");
        set("c.calib_in.peaklevel",s.peak);set("c.calib_out.peaklevel",s.peak);
        chain.parse("c.plugin_name=dc_simple");
        chain.parse("c.dc_simple.g50=[0]");set("c.dc_simple.g80",30*(1/s.ratio-1));
        chain.parse("c.dc_simple.maxgain=[0]");
        chain.parse("c.dc_simple.expansion_threshold=[50]");
        chain.parse("c.dc_simple.expansion_slope=[1]");
        chain.parse("c.dc_simple.limiter_threshold=[90]");
        set("gain.gains",s.gain);
    }
    mhaconfig_t f{};f.channels=2;f.fragsize=128;f.srate=s.rate;f.domain=MHA_WAVEFORM;
    chain.prepare(f);prepared=true;ac.set_prepared(true);
}
Processor::~Processor(){ac.set_prepared(false);if(prepared){try{chain.release();}catch(...){}}}
void Processor::render(const float* in,float* out,int inch,int outch){
    if(!out||outch<1||outch>2||(in&&(inch<1||inch>2)))throw std::runtime_error("Invalid channel layout");
    for(unsigned f=0;f<128;++f)for(unsigned ch=0;ch<2;++ch)
        wave.value(f,ch)=in ? in[f*inch+std::min<int>(ch,inch-1)] : 0;
    mha_wave_t* result=nullptr;chain.process(&wave,&result);
    if(!result||result->num_channels!=2||result->num_frames!=128)throw std::runtime_error("Unexpected plugin output");
    for(unsigned f=0;f<128;++f)for(int ch=0;ch<outch;++ch){
        const float v=value(result,f,ch);
        if(!std::isfinite(v))throw std::runtime_error("Non-finite plugin output");
        out[f*outch+ch]=v;
    }
}
Engine::Engine(){check(Pa_Initialize());}
Engine::~Engine(){stop();Pa_Terminate();}
void Engine::refreshDevices(){stop();check(Pa_Terminate());check(Pa_Initialize());}
void Engine::stop(){if(stream){Pa_AbortStream(stream);Pa_CloseStream(stream);stream=nullptr;}processor.reset();inputPeak=0;outputPeak=0;}
bool Engine::running() const{return stream&&Pa_IsStreamActive(stream)==1;}
double Engine::latencyMs() const {const auto* i=stream?Pa_GetStreamInfo(stream):nullptr;return i?1000*(i->inputLatency+i->outputLatency):0;}
void Engine::start(const Settings& s){
    stop();settings=s;phase=0;currentVolume=0;fault=0;xruns=0;blocks=0;
    const auto* out=Pa_GetDeviceInfo(s.output);
    const auto* in=s.tone?nullptr:Pa_GetDeviceInfo(s.input);
    if(!out||out->maxOutputChannels<1||(!s.tone&&(!in||in->maxInputChannels<1)))
        throw std::runtime_error("入出力デバイスを選択してください．");
    outputChannels=std::min(2,out->maxOutputChannels);inputChannels=in?std::min(2,in->maxInputChannels):0;
    PaStreamParameters op{s.output,outputChannels,paFloat32,out->defaultLowOutputLatency,nullptr};
    PaStreamParameters ip{s.input,inputChannels,paFloat32,in?in->defaultLowInputLatency:0,nullptr};
    check(Pa_IsFormatSupported(in?&ip:nullptr,&op,s.rate));
    processor=std::make_unique<Processor>(s);
    try {check(Pa_OpenStream(&stream,in?&ip:nullptr,&op,s.rate,128,paClipOff,callback,this));check(Pa_StartStream(stream));}
    catch(...){stop();throw;}
}
int Engine::callback(const void* input,void* output,unsigned long frames,const PaStreamCallbackTimeInfo*,PaStreamCallbackFlags flags,void* ptr){
    auto& e=*static_cast<Engine*>(ptr);auto* out=static_cast<float*>(output);
    if(flags)e.xruns.fetch_add(1,std::memory_order_relaxed);
    if(frames!=128){std::fill(out,out+frames*e.outputChannels,0);e.fault=1;return paAbort;}
    float tone[256];const float* in=static_cast<const float*>(input);int inch=e.inputChannels;
    if(e.settings.tone){
        inch=2;in=tone;
        for(int f=0;f<128;++f){tone[2*f]=tone[2*f+1]=0.05f*std::sin(e.phase);e.phase+=2*3.141592653589793*440/e.settings.rate;if(e.phase>2*3.141592653589793)e.phase-=2*3.141592653589793;}
    }
    float ip=0,op=0;
    if(in)for(int i=0;i<128*inch;++i)ip=std::max(ip,std::abs(in[i]));
    try{e.processor->render(in,out,inch,e.outputChannels);}catch(...){std::fill(out,out+frames*e.outputChannels,0);e.fault=2;return paAbort;}
    const float target=e.audible.load()?e.volume.load():0;
    for(int f=0;f<128;++f){
        e.currentVolume+=(target-e.currentVolume)*0.01f;
        for(int ch=0;ch<e.outputChannels;++ch){
            float& v=out[f*e.outputChannels+ch];v=std::clamp(v*e.currentVolume,-0.95f,0.95f);op=std::max(op,std::abs(v));
        }
    }
    e.inputPeak.store(ip,std::memory_order_relaxed);e.outputPeak.store(op,std::memory_order_relaxed);e.blocks.fetch_add(1,std::memory_order_relaxed);
    return paContinue;
}
