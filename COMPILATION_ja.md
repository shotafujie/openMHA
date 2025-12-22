# 開発者向けコンパイル手順

Windows、macOS、LinuxでのコンパイルバイナリパッケージのインストールについてはINSTALLATION.mdを参照してください。openMHA自体を変更したい場合を除き、自分でopenMHAをコンパイルする必要はありません。

このガイドでは、開発者向けにオリジナルソースコードからopenMHAをコンパイルする方法を説明します。

**[English version is here / 英語版はこちら](COMPILATION.md)**

**[READMEに戻る](README_ja.md)**

---

## 目次

- [I. Linuxでのソースからのコンパイル](#i-linuxでのソースからのコンパイル)
- [II. macOSでのソースからのコンパイル](#ii-macosでのソースからのコンパイル)
- [III. 64ビットWindowsでのコンパイル（上級者向け）](#iii-64ビットwindowsでのコンパイル上級者向け)
- [IV. Linuxでのドキュメント再生成](#iv-linuxでのドキュメント再生成)

---

## I. Linuxでのソースからのコンパイル

### Linux前提条件

64ビット版のUbuntu 20.04以降、またはDebian Busterを実行しているBeaglebone Black。

以下のソフトウェアパッケージがインストールされている必要があります：
- g++（最小バージョン：g++ 7）
- make
- libsndfile1-dev
- libjack-jackd2-dev
- jackd2
- portaudio19-dev
- liblo-dev
- liblsl
- libeigen3-dev
- libtorch-dev

### Linuxでのコンパイル

GitHubからopenMHAをクローンし、ターミナルで以下を入力してコンパイルします：

```bash
git clone https://github.com/HoerTech-gGmbH/openMHA
cd openMHA
./configure && make
```

### Linuxでの自己コンパイルしたopenMHAのインストール

ソースコードと一緒に非常にシンプルなインストールルーチンが提供されています。関連するバイナリとライブラリを収集するには以下を実行します：

```bash
make install
```

make変数PREFIXを設定して、希望のインストール場所を指定できます。デフォルトのインストール場所は「.」（現在のディレクトリ）です。

その後、openMHAインストールディレクトリをライブラリのシステム検索パスに追加する必要があります：

```bash
export LD_LIBRARY_PATH=<YOUR-MHA-DIRECTORY>/lib:$LD_LIBRARY_PATH
```

また、実行ファイルの検索パスにも追加します：

```bash
export PATH=<YOUR-MHA-DIRECTORY>/bin:$PATH
```

上記の2つの設定の代わりに、openMHAのbinディレクトリにあるthismha.shスクリプトをソースすることで、現在のシェルに対してこれらの変数を正しく設定できます：

```bash
source <YOUR-MHA-DIRECTORY>/bin/thismha.sh
```

これでopenMHAコマンドラインアプリケーションを呼び出せます。以下のコマンドで簡単なテストを行います：

```bash
mha ? cmd=quit
```

これにより、プラグインがロードされていないopenMHAのデフォルト設定が表示されます。

### Linuxでの自己コンパイルしたopenMHAのテスト

#### ユニットテストによるテスト

```bash
sudo apt install libboost-dev cmake
make unit-tests
```

#### システムテストの実行

Ubuntu 20.04を使用している場合、`/usr/share/octave/5.2.0/m/java/java.opts`ファイルを編集または作成し、以下の行が含まれていることを確認してください：

```
-Djdk.lang.processReaperUseDefaultStackSize=true
```

これはUbuntu 20.04のOctaveパッケージのエラーを回避するためです。詳細は https://savannah.gnu.org/bugs/?59310 を参照してください。その後：

```bash
sudo make install octave-signal default-jre-headless
./configure
make test
```

Octaveをインストールする代わりに、Signal Processing Toolbox付きのMatlabを使用できます。

これらのテストには、openMHAソースコードが変更されてgitにチェックインされていない場合、または異なるコンポーネントが異なるgitコミットからコンパイルされた場合に失敗する再現性チェックが含まれています。

---

## II. macOSでのソースからのコンパイル

### macOS前提条件

- macOS 14.4（他のバージョンでも動作する可能性があります）
- 以下のパッケージがインストールされたHomebrew：
  - `brew install jack`
  - `brew install libsndfile pkgconfig portaudio liblo eigen pytorch`
  - `brew install labstreaminglayer/tap/lsl`
- XCodeコマンドラインツール

### macOSでのコンパイル

GitHubからopenMHAをクローンし、ターミナルで以下を入力してコンパイルします：

```bash
git clone https://github.com/HoerTech-gGmbH/openMHA
cd openMHA
./configure && make
```

### macOSでの自己コンパイルしたopenMHAのインストール

ソースコードと一緒に非常にシンプルなインストールルーチンが提供されています。関連するバイナリとライブラリを収集するには以下を実行します：

```bash
make install
```

make変数PREFIXを設定して、希望のインストール場所を指定できます。デフォルトのインストール場所は「.」（現在のディレクトリ）です。

その後、openMHAライブラリインストールディレクトリをopenMHAのライブラリ検索パスに追加する必要があります：

```bash
export MHA_LIBRARY_PATH=<YOUR-MHA-DIRECTORY>/lib
```

また、実行ファイルの検索パスにも追加します：

```bash
export PATH=<YOUR-MHA-DIRECTORY>/bin:$PATH
```

上記の2つの設定の代わりに、openMHAのbinディレクトリにあるthismha.shスクリプトをソースすることで、現在のシェルに対してこれらの変数を正しく設定できます：

```bash
source <YOUR-MHA-DIRECTORY>/bin/thismha.sh
```

これでopenMHAコマンドラインアプリケーションを呼び出せます。以下のコマンドで簡単なテストを行います：

```bash
mha ? cmd=quit
```

これにより、プラグインがロードされていないopenMHAのデフォルト設定が表示されます。

### macOSでの自己コンパイルしたopenMHAのテスト

#### ユニットテストによるテスト

以下の追加Homebrewパッケージをインストールします：
- brew install boost
- brew install cmake

その後：

```bash
make unit-tests
```

#### システムテストの実行

以下の追加Homebrewパッケージをインストールします：
- brew install openjdk
- brew install octave

Octave内で、Octaveパッケージ「control」と「signal」をインストールします。例：

```
pkg install -forge control signal
```

（上記は出力がほとんどなく長時間かかります。完了するまで待ってください。）

代替として、Signal Processing Toolbox付きのMatlabを使用できます。

その後、シェルでopenMHAディレクトリに移動し：

```bash
./configure
make test
```

これらのテストには、openMHAソースコードが変更されてgitにチェックインされていない場合、または異なるコンポーネントが異なるgitコミットからコンパイルされた場合に失敗する再現性チェックが含まれています。

---

## III. 64ビットWindowsでのコンパイル（上級者向け）

### Windows前提条件

- MSYS2ホームページ https://www.msys2.org/ から直接 **MSYS2インストーラ** を取得
  - 64ビットWindows用のインストーラはmsys2-x86_64-*releasedate*.exeという名前です。*リリース日はyyyymmdd形式*
- http://jackaudio.org からJack Audio Connection Kitを取得（Windows用64ビットインストーラを使用）
- 両方のインストーラを実行
- これらのツールの古いバージョンがインストールされていてアップグレードが失敗した場合、Windowsのプログラムの追加と削除で古いバージョンをアンインストールし、最新バージョンをインストールしてください

### Windows準備

スタートメニューから **MSYS2 MinGW 64-bit** を実行します（インストール完了後に自動的に開かなかった場合）。ターミナルで、以下を使用してベースパッケージを更新します：

```bash
pacman -Syu
```

プロンプトが表示されたらターミナルを閉じます。

スタートメニューから **MSYS2 MinGW 64-bit** ターミナルを再起動し、以下を入力します：

```bash
pacman -Su
```

openMHAビルド依存関係をインストールします：

```bash
pacman -S msys/git mingw64/mingw-w64-x86_64-gcc msys/make tar
pacman -S mingw64/mingw-w64-x86_64-boost openbsd-netcat
pacman -S mingw-w64-x86_64-libsndfile mingw-w64-x86_64-portaudio
pacman -S mingw64/mingw-w64-x86_64-nsis mingw-w64-x86_64-eigen3 msys/wget
pacman -S msys/unzip msys/zip dos2unix mingw64/mingw-w64-x86_64-curl
pacman -S mingw-w64-x86_64-liblo
```

Jack for Windowsの開発リソースをMSYS2 MinGW64ツールチェーンが見つけられるディレクトリにコピーします（プロセスでインポートライブラリの名前を変更）：

```bash
cp -rv /c/Program*Files/Jack2/include/* /mingw64/include/
cp /c/Program*Files/Jack2/lib/libjack64.dll.a /mingw64/lib/libjack.dll.a
```

openMHAにはliblslが必要です。MinGWバージョンをインストールします：

```bash
wget https://github.com/HoerTech-gGmbH/liblsl/releases/download/v1.14.0-htch/liblsl-1.14.0-MinGW64.zip
unzip -d /mingw64 liblsl-1.14.0-MinGW64.zip
rm liblsl-1.14.0-MinGW64.zip
```

### Windowsコンパイル

Windowsスタートメニューからにnv64 bashシェルを起動します。GitHubからopenMHAをクローンし、ターミナルで以下を入力してコンパイルします：

```bash
git clone https://github.com/HoerTech-gGmbH/openMHA
cd openMHA
./configure && make install
```

コンパイルには時間がかかる場合があります。

Windowsで自己コンパイルしたopenMHAを起動するには：
1. MSYS2ターミナルでMinGW-64 bashシェルを起動
2. openMHA/binディレクトリに移動
3. 以下を入力してmha実行をテスト：
   ```bash
   ./mha.exe ? cmd=quit
   ```

この手順に従わないと、MHAが必要なすべてのDLLを見つけられない場合があります。

### Windowsでの自己コンパイルしたopenMHAのテスト

#### Windowsでの既知の問題

* 多くの自動テスト（例：プラグインlsl2acをテストするユニットテスト）は、テスト実行中にネットワーク通信を使用します。これにより、制限的なファイアウォールまたはネットワーク設定のWindowsマシンでテストが失敗またはハングするなどの問題が発生する可能性があります。
* libtorchを使用するopenMHAプラグインはWindowsでコンパイルされません。openMHAはMinGWツールチェーンを使用してコンパイルされますが、これはlibtorchライブラリと互換性がありません。

#### ユニットテストによるテスト

```bash
pacman -S mingw-w64-x86_64-cmake
make unit-tests
```

#### システムテストの実行

- https://jdk.java.net/ から64ビット版のopenJDK Javaをインストール
- openJDKインストールの`bin`ディレクトリをシステムPATHに追加し、JAVA_HOME環境変数をそのbinディレクトリの親ディレクトリを指すように作成
- http://octave.org から64ビットWindows用Octaveをインストール
- MSYS2ターミナルでMinGW-64 bashシェルを起動
- **openMHA/mha/mhatest**ディレクトリに移動
- 以下を入力してOctaveを起動（正しいバージョンのOctaveを挿入）：

```bash
/c/Octave/Octave->>version<</mingw64/bin/octave-gui.exe --gui
```

- Octave内で、以下のコマンドでopenMHAシステムテストを実行：

```
set_environement; run_all_tests
```

---

## IV. Linuxでのドキュメント再生成

さまざまな対象読者向けのユーザーマニュアルがPDF形式でこのリリースに同梱されています。これらのファイルは、ターミナルで`./configure && make doc`を入力することで再生成することもできます（config.mkファイルがまだ作成されていない場合のみ./configureが必要です）。新しいマニュアルは./mha/doc/ディレクトリに作成されます。また、HTML Doxygenドキュメントが./mha/doc/mhadoc/html/に生成されます。

まず、LinuxでのopenMHAコンパイルの依存関係をすべてインストールしてください。ドキュメントを再作成するには、以下の追加前提条件が必要です：

- Ubuntu 20.04またはUbuntu 22.04
- doxygen
- xfig
- graphviz
- texlive
- texlive-latex-extra
- texlive-font-utils

---

## 関連ドキュメント

- [README（日本語）](README_ja.md)
- [インストールガイド（日本語）](INSTALLATION_ja.md)
- [README (English)](README.md)
- [Installation Guide (English)](INSTALLATION.md)
