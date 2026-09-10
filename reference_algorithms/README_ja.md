# リファレンスアルゴリズム

[原文](README.md)の日本語訳です．対応：上流 `0b9f087e`．参考文献の完全な書誌表記は原文にあります．

このディレクトリは，文献に基づく信号処理アルゴリズムを実装した設定集です．補聴器処理の先行研究，Baumgärtelほか（2015）「Comparing Binaural Pre-processing Strategies I: Instrumental Evaluation」（Trends in Hearing，19，DOI: 10.1177/2331216515617916）と，Hendrikse，Grimm，Hohmann（2020）「Evaluation of the Influence of Head Movement on Hearing Aid Algorithm Performance Using Acoustic Simulations」（Trends in Hearing，24，1–20，DOI: 10.1177/2331216520916682）で使用されています．

## 補聴器とマイクの配置

設定は `HATS_BTE.png` に示す両耳の耳掛け型（BTE）補聴器を想定します．各補聴器に前・中央・後の3本のマイクがあり，図中の距離の単位はmmです．左右で対応するマイク間の距離は164 mmです．詳細はKayserほか「Database of Multichannel In-Ear and Behind-the-Ear Head-Related and Binaural Room Impulse Responses」，EURASIP Journal on Advances in Signal Processing，Volume 2009，Article ID 298605，10ページを参照してください．原文の著者年は2019，巻年は2009と記載されています．

## MATLAB／Octave用ツール

`mfiles` ディレクトリの `mha_process_ref_algo.m` を使うと，リファレンス設定で音声を処理できます．

## アルゴリズム一覧

入力チャンネルは表の順序で与えます．

| 設定名 | 処理 | 入力チャンネル順 | サンプルレート |
| --- | --- | --- | --- |
| delaysub | 遅延減算ビームフォーマー | 左前，右前，左後，右後 | 48000 Hz |
| Elko1995_ADM | 両側の適応差動マイク | 左前，右前，左後，右後 | 44100 Hz |
| Rohdenburg2007_beam | 両耳ビームフォーマー | 左前，右前，左中央，右中央，左後，右後 | 16000 Hz |
| Baumgaertel2015_AMVDR | 適応MVDRビームフォーマー | 左前，右前，左後，右後 | 16000 Hz |
| Breithaupt2008_SCNR | 単一チャンネル雑音低減 | 左前，右前 | 16000 Hz |
| Grimm2009_coherence | 両耳コヒーレンスフィルター | 左前，右前 | 48000 Hz |

Elko1995_ADMはElko & Pong（1995）「A simple adaptive first-order differential microphone」，IEEE Workshop on Applications of Signal Processing to Audio and Acoustics，169–172ページに基づきます．

Rohdenburg2007_beamはRohdenburg，Hohmann，Kollmeier（2007）「Robustness analysis of binaural hearing aid beamformer algorithms by means of objective perceptual quality measures」，同ワークショップ，315–318ページに基づきます．

Baumgaertel2015_AMVDRは冒頭のBaumgärtelほか（2015）に基づきます．Hendrikseほか（2020）で使用された実装には，アルゴリズム開発者Daniel Marquardtとのやり取りを通して行ったバグ修正が含まれます．

Breithaupt2008_SCNRはBreithaupt，Gerkmann，Martin（2008）「A novel a priori SNR estimation approach based on selective cepstro-temporal smoothing」，ICASSP 2008，4897–4900ページに基づきます．

Grimm2009_coherenceはGrimm，Hohmann，Kollmeier（2009）「Increase and subjective evaluation of feedback stability in hearing aids by a binaural coherence-based noise reduction scheme」，IEEE Transactions on Audio, Speech, and Language Processing，17(7)，1408–1419ページに基づきます．
