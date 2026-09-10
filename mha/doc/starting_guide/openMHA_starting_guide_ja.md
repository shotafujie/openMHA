# openMHA スタートガイド

> この文書は [openMHA_starting_guide.tex](openMHA_starting_guide.tex) の日本語訳です。
> [English version (PDF)](https://www.openmha.org/docs/openMHA_starting_guide.pdf)

翻訳対応：openMHA 4.18.1（上流 `0b9f087e`）．原文はMATLAB／OctaveのGUI操作も含みます．C++だけで進める場合は [C++開発ガイド](../../../docs/CPP_DEVELOPMENT_ja.md) を参照してください．

Copyright &copy; 2005-2021 HörTech gGmbH, Oldenburg  
Copyright &copy; 2021-2026 Hörzentrum Oldenburg gGmbH

---

## 目次

1. [はじめに](#1-はじめに)
2. [必要要件](#2-必要要件)
3. [はじめの一歩](#3-はじめの一歩)
4. [ステップバイステップ演習: ゲイン適用](#4-ステップバイステップ演習-ゲイン適用)
5. [Octave/Matlab GUI で周波数シフターを制御する](#5-octavematlab-gui-で周波数シフターを制御する)
6. [Octave/Matlab GUI でダイナミックコンプレッションを制御する](#6-octavematlab-gui-でダイナミックコンプレッションを制御する)
7. [AC 変数を使う](#7-ac-変数を使う)
8. [自分で設定スクリプトを書く](#8-自分で設定スクリプトを書く)

---

## 1. はじめに

HörTech **open Master Hearing Aid**（openMHA）は、標準的なコンピュータハードウェア上で補聴器の信号処理をリアルタイムに実行できる開発・評価用ソフトウェアプラットフォームです。音声入力から出力までの遅延を低く抑えることが可能です。

### 1.1 このマニュアルについて

このマニュアルは、openMHA を使い始める際の最初のステップについて説明します。openMHA の目的と基本構造の概要を説明した後、openMHA コマンドラインアプリケーションのインストールと起動方法をガイドします。次に、いくつかの基本的な設定と、それを実行するためのステップバイステップの手順を示し、openMHA の制御方法について最初の理解を得られるようにします。さらに、Jack Audio Connection Kit（JACK）との連携、Matlab/Octave 内での openMHA の起動、および独自の設定を記述するための基本的な手順など、openMHA の操作に役立つツールを紹介します。

### 1.2 構造

openMHA は4つの主要コンポーネントに分けることができます:

- **openMHA コマンドラインアプリケーション**（MHA）
- **信号処理プラグイン**（plugins）
- **オーディオ入出力モジュール**（IO）
- **openMHA ツールボックスライブラリ**（libopenmha）

図「open Master Hearing Aidの階層構造」は[原文PDF](https://www.openmha.org/docs/openMHA_starting_guide.pdf)を参照してください．図のPDFはドキュメント生成時の成果物で，このソースチェックアウトには含まれません．

**MHA コマンドラインアプリケーション** はプラグインホストとして動作します。信号処理プラグインとオーディオ入出力モジュール（IO）をロードできます。さらに、コマンドラインの設定インターフェースと TCP/IP ベースの設定インターフェースを提供します。異なる IO モジュールが存在します: リアルタイム信号処理には、一般的に openMHA の *MHAIOJack* モジュールが使用され、Jack Audio Connection Kit（JACK）へのインターフェースを提供します。*MHAIOFile* モジュールはオーディオファイルアクセスを、*MHAIOTCP* は TCP/IP ベースの信号交換を提供します。

**openMHA プラグイン** はオーディオ信号処理機能と信号ハンドリングを提供します。通常、1つの openMHA プラグインが1つの特定のアルゴリズムを実装します。複数の openMHA プラグインを組み合わせることで、完全な仮想補聴器信号処理を実現できます。

### 1.3 プラットフォームサービスと規約

openMHA プラットフォームは、プラグインに実装されたアルゴリズムに対していくつかのサービスと規約を提供し、補聴器アルゴリズムの開発に特に適した環境を実現しつつ、汎用的な信号処理もサポートしています。

他の多くのプラグインホストと同様に、openMHA のオーディオ信号はフラグメント（断片）単位で処理されます。つまり、入力信号ストリームの定義された長さのチャンク単位で処理されます。ただし、プラグインはオーディオ信号を時間領域のオーディオサンプルのフラグメントとして伝搬することに限定されず、短時間フーリエ変換（STFT）領域、つまりオーディオ信号フラグメントのスペクトルとして伝搬することも可能です。これにより、すべてのプラグインが独自の STFT 分析と合成を行う必要がなくなります。許容可能な音質の STFT 分析と再合成は常にアルゴリズム的な遅延を導入するため、処理チェーン全体で十分に低い遅延を達成するには、STFT データの共有が補聴器信号処理プラットフォームにとって不可欠です。

プラグイン間で非オーディオ情報を共有するには、**アルゴリズム通信（AC）変数** を使用します。AC 変数についてはこのマニュアルの[第7章](#7-ac-変数を使う)で詳しく説明します。

---

## 2. 必要要件

### 2.1 必要なプログラム

**以下のソフトウェアをインストールしてください:**

- **オペレーティングシステム**
  - **Linux:** Ubuntu 22.04以降
  - **Windows:** Windows 11
  - **macOS:** Homebrew導入済みのmacOS

- **openMHA**  
  https://github.com/HoerTech-gGmbH/openMHA/blob/master/INSTALLATION.md

- **OctaveとOpenJDK，またはMATLAB**
  - **Octave:**
    - **Linux:**  
      `sudo apt install octave-signal default-jre-headless`
    - **Windows:**  
      https://www.gnu.org/software/octave/download.html
      OpenJDKは，例えば https://adoptium.net/ のTemurinを導入します．
    - **macOS:**  
      Homebrew で openMHA をインストールする際に推奨依存関係として自動的にインストールされます。
  - **Matlab:**  
    https://www.mathworks.com/downloads/

- **JACK Audio Connection Kit**
  - **Linux:**  
    `sudo apt install jackd2 qjackctl`
  - **Windows:**  
    http://jackaudio.org/downloads/
  - **macOS:**  
    Homebrew で openMHA をインストールする際に依存関係として自動的にインストールされます。

### 2.2 最新バージョンへのアップデート

このガイドはopenMHA 4.18.1に対応しています．インストール済みの場合は，最新版を使用していることを確認してください．

- **Windows**  
  GitHubの最新リリースから，使用するシステム向けのWindowsリリースファイルを取得し，インストール手順を繰り返してください．
  インストール手順: https://github.com/HoerTech-gGmbH/openMHA/blob/master/INSTALLATION.md

- **macOS**  
  ターミナルで次のコマンドを実行し，Homebrew経由で更新します．
  ```
  brew update
  brew upgrade
  ```
  インストール手順: https://github.com/HoerTech-gGmbH/openMHA/blob/master/INSTALLATION.md

- **Linux**  
  GitHubの最新リリースから，使用するシステム向けのLinuxリリースファイルを取得し，[インストール手順](../../../INSTALLATION_ja.md)を繰り返してください．

### 2.3 システム固有の設定

- **Linux**
  - ユーザーを `audio` グループに追加してください（`YourUserName` を実際のユーザー名に置き換えてください）:  
    `sudo adduser YourUserName audio`
  - 低遅延 Linux カーネルをインストールしてください:  
    `sudo apt install linux-image-lowlatency`
  - 新しいカーネルを使用し、グループメンバーシップを有効にするためにコンピュータを再起動してください。

- **Windows, macOS**  
  Octave/Matlab のインストールが Java を利用できることを確認してください。Octave/Matlab のコマンドウィンドウで以下を実行してテストします:  
  `javaclasspath`  
  "STATIC JAVA PATH ... DYNAMIC JAVA PATH ..." と応答されれば、Java は正しく設定されています（警告が表示されても問題ありません）。  
  エラーで応答される場合は、コンピュータに適切な Java Runtime Environment をインストールし、Octave/Matlab を再起動して再度テストしてください。詳細は Octave/Matlab のドキュメントを参照してください。

---

## 3. はじめの一歩

### 3.1 openMHA の起動

openMHA とその依存関係がインストールされたら（[2.1節](#21-必要なプログラム)参照）、以下の方法で openMHA を起動できます:

#### Linux

**ターミナル** を開いて以下を入力してください:

```
mha --interactive
```

#### Windows

**ターミナル** を開きます:
1. **Windows + R** を押す
2. `cmd` と入力して **Enter** を押す

ターミナルウィンドウに以下を入力します:

```
mha --interactive
```

#### macOS

**Command + Space** を押して Spotlight 検索を開き、"terminal" と入力して **Enter** を押します。ターミナルに以下を入力してください:

```
mha --interactive
```

![Linux ターミナル: mha --interactive を入力](mha_interactive.png)
*図: Linux ターミナル: `mha --interactive` を入力*

---

**注意**: ターミナルのカレントディレクトリが openMHA プロセスのカレントワーキングディレクトリ（CWD）になります。openMHA は相対ファイル名を CWD からの相対パスとして解決します。このガイドの以下の例で、ファイルが見つからないというエラーが openMHA から発生した場合は、CWD からファイル名が解決できるかどうかを確認してください。ファイル検索の問題を修正するには、openMHA を再起動する前にターミナルの CWD を変更するか、正しい絶対パスまたは相対パスを含むようにファイル名を修正してください。

**openMHA の起動に成功しました。次のセクションでは、簡単な設定の使い方をステップバイステップで説明します。**

このチャプターで起動した openMHA を終了するには、ターミナルに以下を入力してください:

```
cmd=quit
```

---

## 4. ステップバイステップ演習: ゲイン適用

### はじめの手順

openMHA の簡単なユースケースとして、オーディオ信号にゲインを適用します。`1speaker_diffNoise_2ch.wav` という名前のオーディオファイルにゲイン係数を適用することから始めます。対応するパラメータ（ゲイン係数、入力チャンネル数、フラグメントサイズ、サンプルサイズなど）は手動で設定できますが、この例では既に openMHA 設定ファイルが以下の場所に用意されています:

- **Linux**: `/usr/share/openmha/examples/00-gain`
- **Windows**: `C:\Program Files\openMHA\examples\00-gain`
- **macOS（Intel プロセッサ）**: `/usr/local/share/openmha/examples/00-gain`
- **macOS（ARM プロセッサ）**: `/opt/homebrew/share/openmha/examples/00-gain`

以下は gain_getting_started.cfg ファイルの内容です。各コマンドの前に `#` で始まるコメント行で簡単な説明があります。

**gain_getting_started.cfg:**

```
#The number of channels we want to process
nchannels_in = 2
#Number of frames to be processed in each block.
fragsize = 64
#Sampling rate. Has to be the same as the input file
srate = 44100
#We want to use the plugin "mhachain"
mhalib = mhachain
#Now we need to define input-output backend "iolib"
#Here we decide if the audio should come from a static audio
#file or from e.g. a live input source such as a microphone
#input
#In this case we will use simple static audio files
iolib = MHAIOFile
#The plugin "mhachain" can load multiple plugins and
#will connect them in series which is denoted by "[...]"
#Here we will only use one plugin "gain"
mha.algos=[ gain ]
#Set max and min gain factors in dB
mha.gain.min=-20
mha.gain.max=20
#nchannels_in was set to 2 (see line 2), so we have to define
#two gain factors (left and right)
mha.gain.gains=[ -10 10 ]
#Define the name of the input and output file
#The input file needs to be in the same directory
#as the .cfg file itself
io.in = 1speaker_diffNoise_2ch.wav
io.out = 1speaker_diffNoise_2ch_OUT.wav
```

このガイドでは openMHA インストーラーに含まれるサンプルファイルを使用します。これらは読み取り専用のディレクトリにインストールされるため、使用する前にサンプルを書き込み可能な場所にコピーする必要があります。以下の手順に従ってください:

1. 実行中のすべての openMHA プロセスを **終了** する

2. インストールディレクトリから examples フォルダを **コピー** する  
   （例: /usr/share/openmha/examples/）  
   （お使いの OS に応じた上記リストのパスを参照してください）

   ![インストールディレクトリからサンプルフォルダをコピー](copy_examples.png)
   *図: 保護されたディレクトリからサンプルフォルダをコピー*

3. 書き込み可能なディレクトリ内のフォルダ（例: ホームディレクトリ）にサンプルを **貼り付け** る

   ![書き込み可能なディレクトリにサンプルを貼り付け](paste_examples.png)
   *図: 保護されていないディレクトリにサンプルを貼り付け*

4. **ターミナル** を開く（[3.1節](#31-openmha-の起動)参照）

5. examples フォルダ内の最初のサンプルのサブディレクトリ **00-gain** に移動する  
   （例: `/home/YourUserName/Documents/examples/00-gain`）
   - `cd ..` で1つ上のフォルダレベルに移動
   - `cd foldername` でサブフォルダに移動
   - **macOS または Linux** のターミナルがカレントディレクトリを表示しない場合は `pwd` と入力

6. `mha --interactive` と入力して **Enter** を押す

### 4.1 ファイル間処理

openMHA をインタラクティブモードで起動し、openMHA コマンドを入力できるようになりました。openMHA のカレントワーキングディレクトリは、書き込み可能な場所にコピーした 00-gain サンプルディレクトリである必要があります。設定ファイル **gain.cfg**（00-gain 内にあります）を読み込むには、以下を入力してください:

```
?read:gain_getting_started.cfg
```

openMHA 信号処理を開始します:

```
cmd=start
```

次に、以下を入力して openMHA を終了します:

```
cmd=quit
```

![インタラクティブモード: 静的オーディオ信号にゲインを適用](static_gain.png)
*図: インタラクティブモード: 静的オーディオ信号にゲインを適用*

**openMHA が 00-gain フォルダ内に "1speaker_diffNoise_2ch_OUT.wav" という2つ目の .wav ファイルを作成しました（例: `/home/YourUserName/Documents/examples/00-gain`）。再生して "1speaker_diffNoise_2ch.wav" と比較してみてください。**

### 4.2 JACK 入出力で openMHA を起動する

このセクションでは、前と同じ信号処理を行いますが、サウンドファイルの代わりに JACK サーバーをオーディオバックエンドとして使用します。これにより、例えばマイク入力にリアルタイムでゲインを適用できます。このために `gain_live_getting_started.cfg` 設定ファイルを使用します。

**注意**: この例および以降のすべてのライブ処理例では、小さなバッファサイズでサウンドカードを設定します。お使いのコンピュータ、サウンドカード、オペレーティングシステムの組み合わせでは、これらの設定でドロップアウトなしにサウンドを処理できない場合があります。問題が発生した場合は、より高速なコンピュータを使用するか、オペレーティングシステムをリアルタイムパフォーマンス向けに最適化するか、別のサウンドカードやオペレーティングシステムを使用してみてください。

**gain_live_getting_started.cfg:**

```
#The number of channels we want to process
nchannels_in = 2
#Number of frames to be processed in each block.
fragsize = 64
#Sampling rate. Has to be the same as the input signal of JACK
srate = 44100
#Again, we want to use the plugin "mhachain"
mhalib = mhachain
#Here we will only use one plugin "gain"
mha.algos=[ gain ]
#Set max and min gain factors in dB
mha.gain.min=-20
mha.gain.max=20
#two gain factors (left and right)
mha.gain.gains=[ -10 10 ]
#In this example, we load the IO library that connects
#the MHA to the Jack audio server.
iolib = MHAIOJackdb
# The following variable is used to select the input sound
# channel(s), following the usual Jack nomenclature
io.con_in = [system:capture_1 system:capture_2]
# con_out sets the output channels
io.con_out = [system:playback_1 system:playback_2]
```

JACK サーバーのセットアップと接続を行うには、以下の手順に従ってください:

1. **Jack Audio Connection Kit を起動する**

   - **Linux:**  
     **ターミナル** に `qjackctl` と入力します。
   - **Windows:**  
     **JACK Control** のスタートメニューエントリを使用します。
   - **macOS:**  
     **ターミナル** に `qjackctl` と入力します。求められた場合は、サウンドデバイスへのアクセスを許可してください。

   ![JACK Audio Connection Kit: GUI](jack_gui.png)
   *図: JACK Audio Connection Kit: GUI*

2. **Setup** → **Settings** → 適切な Driver、Interface を選択し、Sample Rate=44100、Frames/Period=64 を設定 → **OK**

   ![Jack GUI: セットアップ](jack_setup.png)
   *図: Jack GUI: セットアップ*

3. **Start** をクリックして JACK サーバーを起動 → *Messages* でエラーがないか確認（適切なドライバ設定を見つけるのが難しい場合があります。異なる設定を試してみてください）

   ![実行中のサーバーを持つ Jack GUI](jack_started.png)
   *図: 実行中のサーバーを持つ Jack GUI*

4. Jack サーバーをテストするには、**Connect** セクションで（内蔵）マイクの入力を Jack サーバーの出力チャンネルに接続します。

   ![Jack GUI: 接続](jack_connection.png)
   *図: Jack GUI: 接続*

   次に進む前にこれらの接続を解除してください。これで JACK サーバーをオーディオバックエンドとして使用できます。

5. **ターミナル** を開く（[3.1節](#31-openmha-の起動)参照）
6. examples フォルダ内の **00-gain** サブディレクトリに移動
7. `mha --interactive` と入力して **Enter** を押す
8. 以下を入力:
   ```
   ?read:gain_live_getting_started.cfg
   ```
9. 以下を入力:
   ```
   cmd=start
   ```

openMHA があなたの音声入力にゲインを適用しています。openMHA を終了するには以下を入力してください:

```
cmd=quit
```

**静的オーディオファイルと Jack を使用したライブ入力の両方で簡単な設定を起動できるようになりました。次のセッションでは、Matlab または Octave を openMHA のユーザーインターフェースとして使用します。**

---

## 5. Octave/Matlab GUI で周波数シフターを制御する

1. 実行中のすべての **mha プロセス** を **終了** する

2. **Matlab または Octave** を開く

3. 環境設定:
   - **Linux:** コマンドウィンドウに以下を入力して LD_LIBRARY_PATH を空に設定:  
     `setenv('LD_LIBRARY_PATH','')`
   - **macOS（Intel プロセッサ）:** コマンドウィンドウに以下を入力:  
     `setenv('PATH', [getenv('PATH') ':/usr/local/bin']);`
   - **macOS（ARM プロセッサ）:** コマンドウィンドウに以下を入力:  
     `setenv('PATH', [getenv('PATH') ':/opt/homebrew/bin']);`

4. Matlab/Octave の **"Current Folder"** コントロールで以下に移動:

   - **Linux:** `/usr/share/openmha/examples/05-frequency-shifting`
   - **Windows:** `C:\Program Files\openMHA\examples\05-frequency-shifting`
   - **macOS（Intel プロセッサ）:** `/usr/local/share/openmha/examples/05-frequency-shifting`
   - **macOS（ARM プロセッサ）:** `/opt/homebrew/share/openmha/examples/05-frequency-shifting`

5. openMHA の Matlab 関数を使用するために、**コマンドウィンドウ** で以下を入力:

   - **Linux:**  
     `addpath('/usr/lib/openmha/mfiles')`
   - **Windows:**  
     `addpath('C:\Program Files\openMHA\mfiles')`
   - **macOS（Intel プロセッサ）:**  
     `addpath('/usr/local/lib/openmha/mfiles/')`
   - **macOS（ARM プロセッサ）:**  
     `addpath('/opt/homebrew/lib/openmha/mfiles/')`

6. 新しい openMHA インスタンスを起動するために以下を入力:  
   `openmha = mha_start;`

7. 設定ファイルを読み込むために以下を入力:  
   `mha_query(openmha,'','read:fshift_live.cfg');`

8. **JACK Control** を使用して **JACK サーバーを起動**  
   （設定: Sample Rate = 44100, Frames/Period = 64）

9. mha プロセスを開始するために以下を入力:  
   `mha_set(openmha, 'cmd', 'start');`

10. **JACK Control**: サウンドカードの "capture" および "playback" チャンネルを MHA の "in" および "out" チャンネルに接続してください。マイクをサウンドカードに接続してください。

11. GUI を起動するために以下を入力:  
    `mhagui_generic(openmha)`
    1. **mha** → サブパーサーを開く
    2. **mhachain** → サブパーサーを開く
    3. **fshift_hilbert** → サブパーサーを開く
    4. **df** → vector\<float\>control を開く

12. GUI で df、fmin、fmax の設定を変更し、処理されたマイク音声を聴いてみてください。スライダーはマウスカーソルや上下矢印キーで操作できるだけでなく、GUI のテキストフィールドに直接数値を入力して **Enter** を押すこともできます。これらの設定は周波数シフターを制御し、どの帯域がどれだけシフトされるかを決定します。

---

## 6. Octave/Matlab GUI でダイナミックコンプレッションを制御する

1. 実行中のすべての **mha プロセス** を **終了** する  
   （ターミナルで `killall mha` と入力すると実行中のすべての mha プロセスを終了できます [Linux/macOS のみ]）

2. **Matlab または Octave** を開く

3. 環境設定:
   - **Linux:** コマンドウィンドウに以下を入力して LD_LIBRARY_PATH を空に設定:  
     `setenv('LD_LIBRARY_PATH','')`
   - **macOS（Intel プロセッサ）:** コマンドウィンドウに以下を入力:  
     `setenv('PATH', [getenv('PATH') ':/usr/local/bin']);`
   - **macOS（ARM プロセッサ）:** コマンドウィンドウに以下を入力:  
     `setenv('PATH', [getenv('PATH') ':/opt/homebrew/bin']);`

4. Matlab/Octave の **"Current Folder"** セクションで以下に移動:

   - **Linux:** `/usr/share/openmha/examples/01-dynamic-compression`
   - **Windows:** `C:\Program Files\openMHA\examples\01-dynamic-compression`
   - **macOS（Intel プロセッサ）:** `/usr/local/share/openmha/examples/01-dynamic-compression`
   - **macOS（ARM プロセッサ）:** `/opt/homebrew/share/openmha/examples/01-dynamic-compression`

5. openMHA の Matlab 関数を使用するために、**コマンドウィンドウ** で以下を入力:

   - **Linux:** `addpath('/usr/lib/openmha/mfiles')`
   - **Windows:** `addpath('C:\Program Files\openMHA\mfiles')`
   - **macOS（Intel プロセッサ）:** `addpath('/usr/local/lib/openmha/mfiles/')`
   - **macOS（ARM プロセッサ）:** `addpath('/opt/homebrew/lib/openmha/mfiles/')`

6. openMHA を起動するために以下を入力:  
   `openmha = mha_start;`

7. 設定を mha に読み込むために以下を入力:  
   `mha_query(openmha,'','read:dynamiccompression_live.cfg');`

8. **JACK Control** を使用して **JACK サーバーを起動**  
   （設定: Sample Rate = 44100, Frames/Period = 64）

9. mha プロセスを開始するために以下を入力:  
   `mha_set(openmha,'cmd','start');`

10. 現在のゲインテーブル `gtdata` と、`gtmin` や `gtstep` などの関連パラメータ（詳細は[プラグインマニュアル](http://www.openmha.org/docs/openMHA_plugins.pdf#subsection.5.1)を参照）を以下で読み出せます:

    ```matlab
    gaintable = mha_get(openmha,'mha.overlapadd.mhachain.dc.gtdata');
    gtmin = mha_get(openmha,'mha.overlapadd.mhachain.dc.gtmin');
    gtstep = mha_get(openmha,'mha.overlapadd.mhachain.dc.gtstep');
    ```

    変数 `gtmin`（最小入力レベル）と `gtstep`（入力レベル増分）はベクトルを期待しますが、先ほどはスカラー値を割り当てました。スカラー値はベクトル変数に割り当てた場合、MHA により長さ1のベクトルとして解釈されます。dc プラグインは `gtmin` と `gtstep` に長さ1のベクトルを許容し、この場合同じ値がすべてのチャンネル/帯域に適用されます。チャンネル/帯域ごとに異なる `gtmin`/`gtstep` の値を設定することも可能で、その場合はチャンネル/帯域数と同じ要素数のベクトルを割り当てます。

11. Matlab で独自のゲインテーブルを設計できます。例: ノイズゲート、圧縮領域、出力制限:

    ```matlab
    gaintable = repmat([-50,30:-2:0,-4:-4:-32],18,1);
    ```

    以下を使用:
    ```matlab
    gtmin = zeros(1,size(gaintable,1));
    gtstep = 4*ones(1,size(gaintable,1));
    ```

    これにより、すべてのチャンネル/帯域で同じ入出力特性が得られます。

12. I/O 特性をプロットする:
    ```matlab
    level_in = ((1:size(gaintable,2))-1) .* gtstep'+gtmin';
    level_out = level_in + gaintable;
    ```

13. ゲインテーブルを適用するために以下を入力:
    ```matlab
    mha_set(openmha,'mha.overlapadd.mhachain.dc.gtdata',gaintable);
    ```

14. Matlab で入出力レベルをプロットするために以下を入力:
    ```matlab
    figure, plot(level_in',level_out')
    ```

    **注意:** mfile ツール **dc_plot_io.m** も使用できます:
    ```matlab
    figure, dc_plot_io(gtmin, gtstep, gaintable, level_in);
    ```

15. Matlab でさらにゲインテーブルを設計できます。例:
    - すべての入力レベルを同じ出力レベルに圧縮する（無限圧縮）:  
      `gaintable_new = 65.*ones(18,1) - level_in;`
    - 高周波帯域のみを圧縮する: ...

16. 新しいゲインテーブルを適用するために以下を入力:
    ```matlab
    mha_set(openmha,'mha.overlapadd.mhachain.dc.gtdata',gaintable_new);
    ```

17. フィッティング GUI は以下を入力して起動できます:  
    `mhacontrol(openmha)`

18. openMHA を以下で停止できます:  
    `mha_set(openmha,'cmd','quit')`

---

## 7. AC 変数を使う

このセクションの目的は、Matlab と組み合わせた AC 変数の扱い方を学ぶことです。

### AC 変数とは？

プラグインアルゴリズムは、現在のオーディオ信号以上の情報を共有する必要がある場合があります。openMHA は、**アルゴリズム通信変数**（**AC 変数**）の形でプラグイン間で任意の種類の追加データを共有するメカニズムを提供することでこれをサポートしています。AC 変数の目的についての詳細は *Application Manual* のセクション 2.2 を参照してください。

---

ここでは2つのライブマイク信号間のコヒーレンスを調べます。JACK サーバーを使用して両方のマイク信号を openMHA に接続します。

1. **JACK Control** を使用して **JACK サーバーを起動**  
   （設定: Sample Rate = 44100, Frames/Period = 64）  
   **注意: このタスクには2つのマイク入力が必要です**

2. Matlab/Octave を起動し、**"Current Folder"** コントロールで以下に移動:

   - **Linux:** `/usr/share/openmha/examples/15-ac-variables`
   - **Windows:** `C:\Program Files\openMHA\examples\15-ac-variables`
   - **macOS（Intel プロセッサ）:** `/usr/local/share/openmha/examples/15-ac-variables`
   - **macOS（ARM プロセッサ）:** `/opt/homebrew/share/openmha/examples/15-ac-variables`

3. Matlab スクリプト **acmatlab.m** を開く

   **acmatlab.m** の最も重要な行を以下に示します:

   ```matlab
   % openMHA プロセスを開始
   openmha = mha_start;
   % 設定ファイルを読み込み
   mha_query(openmha,'','read:coherence_live.cfg');
   % 設定ファイルを開始
   mha_set(openmha,'cmd','start')

   %% 中心周波数のラベル付けと ac_proc のゲイン係数設定

   % 中心周波数のラベル付け
   freqs = mha_get(openmha,'mha.overlapadd.mhachain.coherence.cf');
   % ゲイン係数を dB で設定 - デフォルト値は 6 に設定
   mha_set(openmha,'mha.overlapadd.mhachain.coh_gain.gain.gains',6);
   ```

### 解説

使用される設定は *coherence_live.cfg* です。**mhachain** プラグインを使用して3つのプラグインを直列に接続します:

1. coherence
2. ac_proc:coh_gain
3. acmon

設定ファイル内では以下のように記述されます:

```
mha.overlapadd.mhachain.algos = [coherence ac_proc:coh_gain acmon]
```

各プラグインの目的は以下の通りです:

**coherence:** このプラグインは2つのマイク入力信号間のコヒーレンスを測定します。

**ac_proc:coh_gain:** プラグインの本名は *ac_proc* ですが、ここではエイリアス *coh_gain* が使用されています。このプラグインは *coherence* から受け取った AC 変数データストリームをオーディオ信号として解釈します。プラグイン自体は別のプラグインをロードできます。この場合は gain プラグインがロードされます。ゲイン係数は 6 dB に設定されています。これは AC 変数出力「信号」が 6 dB 増幅されることを意味します。プラグイン ac_proc の外部では、信号は AC 変数ストリームとして提供されます。

**acmon:** このプラグインは受信した AC 変数データストリームをモニター変数に変換するために使用されます。この場合、*coherence* と *ac_proc:coh_gain* の出力が使用されます。

![AC 変数データストリームの模式図](coherence_chain.png)
*図: プラグイン間の AC 変数データストリームの模式図: coherence, ac_proc, acmon*

4. Matlab スクリプト **acmatlab.m** を実行する

   ![Matlab: 周波数の関数としてプロットされたコヒーレンス](ac_variables_coherence.png)
   *図: Matlab: 周波数の関数としてプロットされたコヒーレンス*

この例の目的は、プラグイン ac_proc を使用して、AC 変数データストリームのような本来非オーディオ信号にゲインなどの一般的な信号処理操作を適用できることを示すことです。

---

## 8. 自分で設定スクリプトを書く

このセクションでは、独自の openMHA スクリプトを書く方法をガイドします。そのためにはいくつかの基本パラメータを設定する必要があります。この例では *sine* プラグインを使用するスクリプトを書きます。

まず、以下のパラメータを決定する必要があります:

1. **入力チャンネル数**（`nchannels_in`）

2. **フラグメントサイズ**（`fragsize`）

3. **サンプリングレート（Hz）**（`srate`）

   2チャンネル、サンプリングレート 44.1 kHz の入力ファイルの場合、以下のようになります:

   ```
   #The number of channels we want to process
   nchannels_in = 2
   #Number of frames to be processed in each block.
   fragsize = 64
   #Sampling rate. Has to be the same as the input file
   srate = 44100
   ```

4. **プラグイン:** 次に、`mhalib` 変数でどのプラグインをロードするか MHA に指示する必要があります。冒頭で述べたように、ここでは sine プラグインを例として使用します:

   ```
   #We want to use the plugin "sine"
   mhalib = sine
   ```

5. **設定変数:** 各プラグインには *設定変数* があり、適宜調整できます。各プラグインの設定変数は[プラグインマニュアル](http://www.openmha.org/docs/openMHA_plugins.pdf#subsection.19.3)（sine プラグインの場合）に一覧があります。これらの変数は要件に応じて調整できます。例えばサイン波の周波数（`f`）、RMS レベル（`lev`）、入力信号をサイン波に加算するか完全に置き換えるか（`mode`）などです。

   プラグインは `mhalib = sine` で使用しますが、プラグインの変数は `mha.<variable_name> = value` で変更します。例えば:

   ```
   #Adjust configuration variables
   #frequency
   mha.f = 440
   #RMS Level
   mha.lev = 100
   #Operating mode (can be changed to replace[default])
   mha.mode = mix
   #Channels on which the sine plugin should operate
   mha.channels=[0]
   ```

   ここでは周波数が 440 Hz に、サイン音の RMS レベルが 100 dB に調整されています。動作モードは `mix` に設定されており、入力がサイン信号と混合されます（置き換えではなく）。変数 `channels` は `[0]` に調整されています。これはサインプラグインが最初のチャンネルのみで動作することを意味します。両チャンネルで動作させるには `mha.channels = [0 1]` を使用できます。

6. **オーディオバックエンド:** openMHA はサウンドドライバ、JACK オーディオサーバー、サウンドファイル、ネットワークなど、異なるオーディオバックエンドをサポートしています。IO プラグインライブラリ（`iolib`）を選択することで調整できます。

   静的オーディオファイルの場合: `iolib = MHAIOFile`  
   ライブ JACK 信号の場合: `iolib = MHAIOJack`

   ここでは静的オーディオファイルを使用するため:

   ```
   #In this case we will use simple static audio files
   #For live input use 'MHAIOJack'
   iolib = MHAIOFile
   ```

7. **入力**（`io.in`）

   静的オーディオファイルの場合: `io.in = name_of_file.wav`  
   ライブ JACK 信号の場合: `io.con_in = [system:capture_1 system:capture_2]`（2入力チャンネルの場合）

   ```
   #Define the name of the input file
   #The input file needs to be in the same directory
   #as the .cfg file itself
   io.in = 1speaker_diffNoise_2ch.wav
   ```

   **注意: 入力ファイルは .cfg ファイルと同じディレクトリにある必要があります。そうでない場合は、絶対パスまたは（.cfg ファイルからの）相対パスを使用できます:**
   - `./../Folder/1speaker_diffNoise_2ch.wav`（*相対パス*）
   - `/home/UserName/Folder/1speaker_diffNoise_2ch.wav`（*絶対パス*）

8. **出力**（`io.out`）

   静的オーディオファイルの場合: `io.out = name_of_file_out.wav`  
   ライブ JACK 信号の場合: `io.con_out = [system:playback_1 system:playback_2]`（2出力チャンネルの場合）

   ```
   #Define name of output file
   io.out = 1speaker_diffNoise_2ch_OUT.wav
   ```

### スクリプトの実行方法

1. .cfg ファイルと **同じディレクトリ** で openMHA を起動する
2. `?read:your_script.cfg`
3. openMHA 信号処理を開始:  
   `cmd=start`
4. openMHA を終了するには:  
   `cmd=quit`
