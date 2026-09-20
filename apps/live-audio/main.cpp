// SPDX-License-Identifier: AGPL-3.0-only
#include "engine.hpp"
#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QDoubleSpinBox>
#include <QFormLayout>
#include <QGroupBox>
#include <QLabel>
#include <QPermissions>
#include <QProgressBar>
#include <QPushButton>
#include <QSlider>
#include <QTimer>
#include <QVBoxLayout>
#include <QThread>
#include <cmath>
#include <iostream>
#include <algorithm>
#include <stdexcept>

class Window:public QWidget {
    Engine engine;
    QComboBox *source=new QComboBox,*input=new QComboBox,*output=new QComboBox,*mode=new QComboBox,*rate=new QComboBox;
    QDoubleSpinBox *gain=new QDoubleSpinBox,*cutoff=new QDoubleSpinBox,*ratio=new QDoubleSpinBox,*peak=new QDoubleSpinBox;
    QPushButton *start=new QPushButton("開始"),*stop=new QPushButton("停止"),*apply=new QPushButton("設定を適用"),*refresh=new QPushButton("デバイスを更新");
    QCheckBox *audible=new QCheckBox("音を出す（ヘッドホンを使用）");
    QSlider *volume=new QSlider(Qt::Horizontal);
    QProgressBar *inMeter=new QProgressBar,*outMeter=new QProgressBar;
    QLabel *status=new QLabel("停止中 · デバイスと処理を選んで開始"),*details=new QLabel,*volumeLabel=new QLabel("−20 dB"),*hint=new QLabel;
    bool pending=false;
    Settings settings() const {
        Settings s;s.input=input->currentIndex()<0?-1:input->currentData().toInt();s.output=output->currentIndex()<0?-1:output->currentData().toInt();s.tone=source->currentIndex()==1;
        s.mode=mode->currentIndex();s.rate=rate->currentText().toDouble();s.gain=gain->value();s.cutoff=cutoff->value();s.ratio=ratio->value();s.peak=peak->value();return s;
    }
    void devices(){
        const auto oldIn=input->currentText(),oldOut=output->currentText();input->clear();output->clear();
        const int count=Pa_GetDeviceCount();
        if(count<0){status->setText(Pa_GetErrorText(count));return;}
        for(int i=0;i<count;++i){const auto* d=Pa_GetDeviceInfo(i);const auto* api=Pa_GetHostApiInfo(d->hostApi);
            const auto name=QString::fromUtf8(d->name)+" · "+QString::fromUtf8(api->name);
            if(d->maxInputChannels>0)input->addItem(name,i);if(d->maxOutputChannels>0)output->addItem(name,i);
        }
        int i=input->findText(oldIn);if(i<0)i=input->findData(Pa_GetDefaultInputDevice());if(i>=0)input->setCurrentIndex(i);
        i=output->findText(oldOut);if(i<0)i=output->findData(Pa_GetDefaultOutputDevice());if(i>=0)output->setCurrentIndex(i);
    }
    void controls(bool running){start->setEnabled(!running&&!pending);stop->setEnabled(running||pending);refresh->setEnabled(!running&&!pending);apply->setEnabled(!pending);source->setEnabled(!pending);input->setEnabled(!pending&&source->currentIndex()==0);output->setEnabled(!pending);}
    void launch(){
        try {engine.start(settings());status->setText("処理中 · "+mode->currentText());controls(true);}
        catch(const std::exception& e){status->setText("開始できません："+QString::fromUtf8(e.what()));controls(false);}
    }
    void begin(){
        if(pending)return;
        if(source->currentIndex()==0){
            QMicrophonePermission permission;
            const auto state=qApp->checkPermission(permission);
            if(state==Qt::PermissionStatus::Undetermined){
                pending=true;controls(false);status->setText("マイクの許可を待っています…");
                qApp->requestPermission(permission,this,[this](const QPermission& p){
                    const bool requested=pending;pending=false;controls(false);
                    if(!requested)return;
                    if(p.status()==Qt::PermissionStatus::Granted)launch();
                    else status->setText("マイクが許可されていません．OSのプライバシー設定を確認してください．");
                });return;
            }
            if(state==Qt::PermissionStatus::Denied){status->setText("マイクが許可されていません．OSのプライバシー設定を確認してください．");return;}
        }
        launch();
    }
public:
    Window(){
        setWindowTitle("OpenMHA Live");resize(700,860);
        setStyleSheet("QWidget{font-size:14px;} QWidget#root{background:#f4f6fa;} QGroupBox{background:white;border:1px solid #dce2ec;border-radius:10px;margin-top:16px;padding:18px 12px 12px;} QGroupBox::title{subcontrol-origin:margin;left:16px;color:#35445e;} QPushButton{padding:9px 15px;border:1px solid #c7d2e2;border-radius:6px;background:white;} QPushButton#primary{background:#2468db;color:white;} QLabel#title{font-size:28px;font-weight:700;color:#172b4d;} QProgressBar{border:1px solid #dce2ec;border-radius:4px;text-align:center;height:20px;} QProgressBar::chunk{background:#39a98a;} QComboBox,QDoubleSpinBox{padding:5px;} ");
        setStyleSheet(styleSheet()+"QWidget{font-size:13px;color:#20334d;} QComboBox,QDoubleSpinBox{padding:3px;background:white;} QGroupBox{padding:10px 12px 8px;} QPushButton{padding:6px 12px;} QWidget:disabled{color:#7e8b9d;}");
        setStyleSheet(styleSheet()+"QCheckBox::indicator{width:16px;height:16px;border:1px solid #8293ac;border-radius:3px;background:white;} QCheckBox::indicator:checked{background:#2468db;border:2px solid #174b9e;}");
        setObjectName("root");auto* layout=new QVBoxLayout(this);layout->setContentsMargins(22,16,22,16);layout->setSpacing(8);
        auto* title=new QLabel("OpenMHA Live");title->setObjectName("title");layout->addWidget(title);
        layout->addWidget(new QLabel("マイクの音を，その場で処理して聴く"));
        auto* io=new QGroupBox("01  音声デバイス");auto* form=new QFormLayout(io);
        source->addItems({"マイク入力","テスト音 · 440 Hz"});rate->addItems({"48000","44100"});
        form->addRow("音源",source);form->addRow("入力",input);form->addRow("出力",output);form->addRow("サンプルレート（Hz）",rate);form->addRow(refresh);layout->addWidget(io);
        auto* processing=new QGroupBox("02  処理");auto* pf=new QFormLayout(processing);
        mode->addItems({"ゲイン","ローパス","コンプレッサ"});gain->setRange(-16,16);gain->setSuffix(" dB");cutoff->setRange(80,18000);cutoff->setValue(3000);cutoff->setSuffix(" Hz");ratio->setRange(1,10);ratio->setValue(2);ratio->setSingleStep(0.5);peak->setRange(80,120);peak->setValue(100);peak->setSuffix(" dB SPL");
        pf->addRow("モード",mode);pf->addRow("ゲイン",gain);pf->addRow("ローパス周波数",cutoff);pf->addRow("圧縮比（入力：出力）",ratio);pf->addRow("仮の校正値（入出力共通）",peak);
        hint->setWordWrap(true);hint->setText("変更後は「設定を適用」．処理中は短く停止して再開します．\nコンプレッサの校正値は試作用です．機器を測定した値ではありません．");pf->addRow(hint);pf->addRow(apply);layout->addWidget(processing);
        auto* monitor=new QGroupBox("03  モニター出力");auto* mf=new QFormLayout(monitor);
        volume->setRange(-60,0);volume->setValue(-20);mf->addRow(audible);auto* vl=new QHBoxLayout;vl->addWidget(volume);vl->addWidget(volumeLabel);mf->addRow("出力音量",vl);
        for(auto* meter:{inMeter,outMeter}){meter->setRange(0,60);meter->setValue(0);meter->setFormat("無音");}
        mf->addRow("入力ピーク",inMeter);mf->addRow("出力ピーク",outMeter);layout->addWidget(monitor);
        auto* buttons=new QHBoxLayout;start->setObjectName("primary");buttons->addWidget(start);buttons->addWidget(stop);layout->addLayout(buttons);
        status->setWordWrap(true);details->setWordWrap(true);layout->addWidget(status);layout->addWidget(details);
        connect(refresh,&QPushButton::clicked,this,[this]{try{engine.refreshDevices();devices();status->setText("デバイスを更新しました");}catch(const std::exception& e){status->setText(QString::fromUtf8(e.what()));}});
        connect(start,&QPushButton::clicked,this,[this]{begin();});
        connect(stop,&QPushButton::clicked,this,[this]{pending=false;engine.stop();controls(false);status->setText("停止中");});
        connect(apply,&QPushButton::clicked,this,[this]{const bool active=engine.running();engine.stop();controls(false);if(active)begin();else status->setText("設定済み · 開始すると反映されます");});
        connect(audible,&QCheckBox::toggled,this,[this](bool v){engine.audible=v;});
        connect(volume,&QSlider::valueChanged,this,[this](int db){engine.volume=std::pow(10.f,db/20.f);volumeLabel->setText(QString::number(db)+" dB");});
        const auto updateMode=[this]{cutoff->setEnabled(mode->currentIndex()==1);ratio->setEnabled(mode->currentIndex()==2);peak->setEnabled(mode->currentIndex()==2);};
        connect(mode,&QComboBox::currentIndexChanged,this,[updateMode](int){updateMode();});updateMode();
        connect(source,&QComboBox::currentIndexChanged,this,[this](int i){input->setEnabled(i==0);});
        auto* timer=new QTimer(this);connect(timer,&QTimer::timeout,this,[this]{
            const auto meter=[](QProgressBar* p,float v){const float db=v>1e-6f?20*std::log10(v):-60;p->setValue(std::clamp(int(db+60),0,60));p->setFormat(QString::number(db,'f',1)+" dBFS");};
            meter(inMeter,engine.inputPeak.load());meter(outMeter,engine.outputPeak.load());
            details->setText(QString("128 frames · API報告の往復遅延 %1 ms · バッファ警告 %2 · 処理ブロック %3").arg(engine.latencyMs(),0,'f',1).arg(engine.xruns.load()).arg(engine.blocks.load()));
            if(engine.fault.load()){engine.stop();controls(false);status->setText("音声処理エラーで停止しました．デバイスと設定を確認してください．");engine.fault=0;}
            else if(!pending&&!engine.running())controls(false);
        });timer->start(60);devices();controls(false);
    }
    void testTone(){source->setCurrentIndex(1);begin();}
};

int main(int argc,char** argv){
    QApplication app(argc,argv);app.setApplicationName("OpenMHA Live");app.setStyle("Fusion");
    QPalette palette;
    palette.setColor(QPalette::Window,QColor("#f4f6fa"));palette.setColor(QPalette::WindowText,QColor("#20334d"));
    palette.setColor(QPalette::Base,Qt::white);palette.setColor(QPalette::Text,QColor("#20334d"));
    palette.setColor(QPalette::Button,Qt::white);palette.setColor(QPalette::ButtonText,QColor("#20334d"));
    palette.setColor(QPalette::Highlight,QColor("#2468db"));palette.setColor(QPalette::HighlightedText,Qt::white);app.setPalette(palette);
    if(qEnvironmentVariableIsEmpty("MHA_LIBRARY_PATH"))qputenv("MHA_LIBRARY_PATH",MHA_DEFAULT_PATH);
    try{
        if(app.arguments().contains("--self-test")){
            float in[256],out[256];for(int i=0;i<256;++i)in[i]=0.02f*std::sin(i*0.2f);
            for(int mode=0;mode<3;++mode){Settings s;s.mode=mode;Processor p(s);for(int b=0;b<100;++b){p.render(in,out,2,2);for(float v:out)if(!std::isfinite(v))throw std::runtime_error("Nonfinite DSP output");}
                if(mode==0)for(int i=0;i<256;++i)if(std::abs(in[i]-out[i])>1e-6)throw std::runtime_error("Unity gain mismatch");}
            const auto near=[](float actual,double expected){if(std::abs(actual-expected)>2e-6)throw std::runtime_error("Live DSP numerical comparison failed");};
            {
                Settings s;s.gain=-6;Processor p(s);std::fill(in,in+128,0.1f);p.render(in,out,1,2);
                for(float v:out)near(v,0.1*std::pow(10.,-6./20.));
                p.render(nullptr,out,0,2);for(float v:out)near(v,0);
            }
            {
                Settings s;s.mode=1;Processor p(s);std::fill(in,in+256,0);in[0]=in[1]=1;p.render(in,out,2,2);
                const double a=std::exp(-2*3.141592653589793*s.cutoff/s.rate);
                for(int i=0;i<128;++i){near(out[2*i],(1-a)*std::pow(a,i));near(out[2*i+1],out[2*i]);}
            }
            {
                Settings s;s.mode=2;Processor p(s);std::fill(in,in+256,0.1f);
                for(int b=0;b<500;++b)p.render(in,out,2,2);
                for(float v:out)near(v,std::pow(10.,(65.-100.)/20.));
            }
            std::cout<<"PASS: three modes, unity/-6 dB gain, mono duplication, null input, lowpass impulse, compressor steady state\n";return 0;
        }
        if(app.arguments().contains("--audio-smoke")){
            Engine engine;Settings s;s.tone=true;s.output=Pa_GetDefaultOutputDevice();
            for(int mode=0;mode<3;++mode){
                s.mode=mode;engine.start(s);QThread::msleep(1200);
                if(!engine.running()||engine.fault.load()||engine.blocks.load()<100||engine.inputPeak.load()<0.04f||engine.outputPeak.load()!=0)
                    throw std::runtime_error("Muted audio-device smoke test failed");
                std::cout<<"PASS device mode "<<mode<<": blocks="<<engine.blocks.load()<<", xruns="<<engine.xruns.load()<<", reported latency ms="<<engine.latencyMs()<<"\n";
                engine.stop();if(engine.running())throw std::runtime_error("Stop failed");
            }
            return 0;
        }
        Window window;window.show();if(app.arguments().contains("--test-tone"))QTimer::singleShot(500,&window,[&window]{window.testTone();});
        return app.exec();
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
