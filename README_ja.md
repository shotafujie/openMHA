[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4569575.svg)](https://doi.org/10.5281/zenodo.4569575)
![GitHub](https://img.shields.io/github/license/HoerTech-gGmbH/openMHA)

# openMHA

[Open Master Hearing Aid (openMHA)](https://www.openmha.org)

DOI: [10.5281/zenodo.4569575](https://doi.org/10.5281/zenodo.4569575)

現在のリリース: 4.18.1 (2026-06-06)

翻訳対応：上流 `0b9f087e`．このフォークでのビルド・組み込み手順は [C++開発ガイド](docs/CPP_DEVELOPMENT_ja.md) を参照してください．

**[English version is here / 英語版はこちら](README.md)**

---

## 目次

- [openMHAの内容](#openmhaの内容)
- [出版物での引用](#出版物での引用)
- [インストール](#インストール)
- [使用方法](#使用方法)
- [既知の問題](#既知の問題)
- [商用フィッティングルール](#商用フィッティングルール)
- [リファレンスアルゴリズム](#リファレンスアルゴリズム)
- [個別アルゴリズムの参考文献](#個別アルゴリズムの参考文献)

---

## openMHAの内容

本ソフトウェアには、openMHAツールボックスライブラリ、openMHAフレームワークおよびコマンドラインアプリケーション、openMHAを操作するための各種ツール、そして基本的な補聴器信号処理チェーンを構成するアルゴリズムプラグイン群のソースコードが含まれています。主な機能は以下の通りです：

* キャリブレーション
* 雑音抑制のための両側適応差動マイクロホン [1]
* フィードバック低減と残響除去のための両耳コヒーレンスフィルタ [2]
* 難聴補償のためのマルチバンドダイナミックレンジコンプレッサ [3]
* 空間フィルタリングアルゴリズム：
    * 遅延加算ビームフォーマ
    * MVDRビームフォーマ [4]
* 単一チャンネル雑音低減 [5]
* リサンプリングおよびフィルタプラグイン
* STFT巡回エイリアシング防止
* 適応フィードバックキャンセレーション [6]
* 確率的音源定位 [7]

利用可能なリファレンス実装の一覧については、以下を参照してください。

## 出版物での引用

openMHAを使用した出版物では、このGitHubリポジトリに割り当てられたDOI [10.5281/zenodo.4569575](https://doi.org/10.5281/zenodo.4569575) を使用し、以下のオープンアクセス論文を引用してください：

Hendrik Kayser, Tobias Herzke, Paul Maanen, Max Zimmermann, Giso Grimm, and Volker Hohmann,
Open community platform for hearing aid algorithm research: open Master Hearing Aid (openMHA),
SoftwareX, Volume 17, 2022, 100953, ISSN 2352-7110, [DOI: 10.1016/j.softx.2021.100953](https://doi.org/10.1016/j.softx.2021.100953).

個別のアルゴリズムについては、プラグインドキュメントおよびこのREADME末尾の出版物リストも参照してください。

## インストール

Linux、Windows、macOSでのインストール手順については、[INSTALLATION_ja.md](INSTALLATION_ja.md)（日本語）または [INSTALLATION.md](INSTALLATION.md)（英語）を参照してください。

Cape4allサウンドカード搭載のBeaglebone Black用SDカードイメージは以下で提供しています：
http://mahalia.openmha.org/

## 使用方法

入門ガイドをご覧ください：
http://www.openmha.org/docs/openMHA_starting_guide.pdf

## 既知の問題

### macOS
* macOSのOctaveにはいくつかの既知の問題があります。openMHA GUIはOctaveで正しく動作しない場合があります。代替としてMatlabを使用できます。

## 商用フィッティングルール

openMHAでは、商用補聴器処方ルール *DSLmio 5* および *NAL NL2* を使用してダイナミックコンプレッサのフィッティングを行うことができます。

これらのルールを実装するソフトウェアライブラリは，それぞれの提供元から入手する必要があります．openMHAチームはこれらのライブラリのラッパーを提供しています．ラッパーはopenMHA本体には含まれず，オプションの追加機能です．

詳細については [README_NALNL2_ja.md](README_NALNL2_ja.md) および [README_DSLmio5_ja.md](README_DSLmio5_ja.md) を参照してください．

## リファレンスアルゴリズム

以下の出版物で使用された補聴器用信号処理アルゴリズムを実装したopenMHA設定ファイル群が *reference_algorithms* ディレクトリで利用可能です：

Baumgärtel, R. M., Krawczyk-Becker, M., Marquardt, D., Völker, C.,
Hu, H., Herzke, T., Coleman, G., Adiloğlu, K., Ernst, S. M., Gerkmann, T.,
Doclo, S., Kollmeier, B., Hohmann, V., & Dietz, M. (2015). Comparing
Binaural Pre-processing Strategies I: Instrumental Evaluation. Trends
in hearing, 19.
https://doi.org/10.1177/2331216515617916

および

Hendrikse, M. M. E., Grimm, G., & Hohmann, V. (2020). Evaluation of
the Influence of Head Movement on Hearing Aid Algorithm Performance
Using Acoustic Simulations. Trends in Hearing, 24, 1–20.
https://doi.org/10.1177/2331216520916682

後者の研究で使用された信号を再現するためのデータベースは以下で利用可能です：
https://doi.org/10.5281/zenodo.3621282

利用可能な手法：

* 単一チャンネル雑音低減
* 両耳コヒーレンスフィルタ
* 適応MVDRビームフォーマ
* 両耳ビームフォーマ
* 両側適応差動マイクロホン
* 遅延減算ビームフォーマ

参考文献およびより詳細な情報については、*reference_algorithms* ディレクトリ内の README.md を参照してください。

## 個別アルゴリズムの参考文献

[1] Elko GW, Pong ATN. A Simple Adaptive First-order Differential
Microphone. In: Proceedings of 1995 Workshop on Applications of Signal
Processing to Audio and Accoustics; 1995. p. 169–172.

[2] Grimm G, Hohmann V, Kollmeier B. Increase and Subjective
Evaluation of Feedback Stability in Hearing Aids by a Binaural
Coherence-based Noise Reduction Scheme. IEEE Transactions on Audio,
Speech, and Language Processing. 2009;17(7):1408–1419.

[3] Grimm G, Herzke T, Ewert S, Hohmann V. Implementation and
Evaluation of an Experimental Hearing Aid Dynamic Range Compressor
Gain Prescription. In: DAGA 2015; 2015. p. 996–999.

[4] Adiloğlu K, Kayser H, Baumgärtel RM, Rennebeck S, Dietz M, Hohmann
V. A Binaural Steering Beamformer System for Enhancing a Moving Speech
Source. Trends in Hearing. 2015;19:2331216515618903

[5] Gerkmann T, Hendriks RC. Unbiased MMSE-Based Noise Power
Estimation With Low Complexity and Low Tracking Delay. IEEE
Transactions on Audio, Speech, and Language
Processing. 2012;20(4):1383–1393.

[6] Schepker H, Doclo S, A semidefinite programming approach to
min-max estimation of the common part of acoustic feedback paths in
hearing aids. IEEE Transactions on Audio, Speech, and Language
Processing. 2016;24(2):366-377.

[7] Kayser H, Anemüller J, A discriminative learning approach to
probabilistic acoustic source localization. In: International Workshop
on Acoustic Echo and Noise Control (IWAENC 2014); 2014. p. 100–104.

---

## 関連ドキュメント

- [インストールガイド（日本語）](INSTALLATION_ja.md)
- [コンパイルガイド（日本語）](COMPILATION_ja.md)
- [Installation Guide (English)](INSTALLATION.md)
- [Compilation Guide (English)](COMPILATION.md)
