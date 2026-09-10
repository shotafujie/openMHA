# 開発者向けビルド手順

[英語原文](COMPILATION.md)／対応：openMHA 4.18.1（上流 `0b9f087e`）．

この文書は原文の翻訳です．このフォークでのC++中心の検証手順・制限は [C++開発ガイド](docs/CPP_DEVELOPMENT_ja.md) に記載します．

ビルド済みパッケージのインストールは [INSTALLATION_ja.md](INSTALLATION_ja.md) を参照してください．openMHA自体を変更しない場合，自分でビルドする必要はありません．以下は開発者がソースコードからビルドするための手順です．

## I. Linuxでのビルド

### 前提条件

64ビット版Ubuntu 22.04以降と，次のパッケージが必要です．

- g++，make
- libsndfile1-dev，libjack-jackd2-dev，jackd2，portaudio19-dev
- liblo-dev，liblsl，libeigen3-dev，libtorch-dev

### ビルドとインストール

```sh
git clone https://github.com/HoerTech-gGmbH/openMHA
cd openMHA
./configure --prefix=/usr/local && make
sudo make install
```

`make install` は `./configure` に指定したprefixへインストールします．次で，プラグイン未ロードの標準設定が表示されることを確認します．

```sh
mha '?' cmd=quit
```

訳注：原文の `?` は，zshなどでファイル名展開されないよう引用しています．以下も同様です．

### テスト

Gitクローンのディレクトリ内で実行します．単体テストは次のとおりです．

```sh
sudo apt install libboost-dev cmake
make unit-tests
```

システムテストにはOctaveなどを追加します．

```sh
sudo apt install octave-signal default-jre-headless
./configure
make test
```

訳注：原文の `sudo make install octave-signal default-jre-headless` はパッケージ導入コマンドとして誤記と考えられるため，上では `sudo apt install` に修正しています．

Octaveの代わりにSignal Processing Toolboxを備えたMATLABを使用できます．システムテストには再現性の確認も含まれます．ソースを変更してGitにコミットしていない場合や，異なるコミットからビルドしたコンポーネントを混在させた場合は失敗します．

## II. macOSでのビルド

### 前提条件

Xcode Command Line ToolsとHomebrewが必要です．原文の依存パッケージは次のとおりです．

```sh
brew install jack
brew install libsndfile pkgconfig portaudio liblo eigen pytorch
brew install labstreaminglayer/tap/lsl
```

### ビルドとインストール

```sh
git clone https://github.com/HoerTech-gGmbH/openMHA
cd openMHA
./configure --prefix=/usr/local && make
make install
```

prefixは任意のインストール先へ変更できます．インストール先のライブラリと実行ファイルを検索できるよう設定します．`<YOUR-PREFIX>` は実際のprefixに置き換えてください．

```sh
export MHA_LIBRARY_PATH=<YOUR-PREFIX>/lib
export PATH=<YOUR-PREFIX>/bin:$PATH
mha '?' cmd=quit
```

プラグイン未ロードの標準設定が表示されれば，コマンドラインアプリが起動しています．

### 単体テスト

追加パッケージを導入し，Gitクローンのディレクトリ内で実行します．

```sh
brew install boost cmake
make unit-tests
```

### システムテスト

```sh
brew install openjdk octave
```

Octave内でcontrolとsignalパッケージをインストールします．この処理は出力が少ないまま長時間かかる場合があります．完了まで待ってください．

```matlab
pkg install -forge control signal
```

Signal Processing Toolboxを備えたMATLABでも代用できます．その後，シェルでGitクローンのディレクトリに移動して実行します．

```sh
make test
```

再現性確認が含まれるため，未コミットのソース変更や，異なるコミットでビルドしたコンポーネントの混在で失敗する場合があります．

## III. 64ビットWindowsでのビルド（上級者向け）

### 前提条件と準備

[MSYS2公式サイト](https://www.msys2.org/)から `msys2-x86_64-公開日.exe`（公開日はyyyymmdd形式）を取得してインストールします．旧版があり更新に失敗する場合は，Windowsのアプリの追加と削除から旧版を削除して最新版を導入してください．

以下はx64用です．すべてのシェルコマンドをMSYS2 UCRT64で実行します．ARM向けではucrt64をclangarm64へ置き換えます．

スタートメニューからMSYS2 UCRT64を開きます．

```sh
pacman -Syu
```

要求されたらターミナルを閉じ，再度MSYS2 UCRT64を開いて実行します．

```sh
pacman -Su
pacman -S dos2unix git make openbsd-netcat tar unzip wget zip mingw-w64-ucrt-x86_64-boost mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-libsndfile mingw-w64-ucrt-x86_64-jack2 mingw-w64-ucrt-x86_64-nsis mingw-w64-ucrt-x86_64-eigen3 mingw-w64-ucrt-x86_64-curl mingw-w64-ucrt-x86_64-liblo mingw-w64-ucrt-x86_64-portaudio mingw-w64-ucrt-x86_64-7zip mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-ninja
cp /ucrt64/lib/libjack64.dll.a /ucrt64/lib/libjack.dll.a
```

必要なliblslのMinGW版をビルドしてインストールします．

```sh
git clone -b main https://github.com/sccn/liblsl
mkdir -p liblsl/build
prefix=/ucrt64
cmake -S liblsl -B liblsl/build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$prefix" -DLSL_UNITTESTS=ON -DLSL_OPTIMIZATIONS=OFF -G Ninja
cmake --build liblsl/build --target install --config Release -j --verbose
```

### ビルドと起動

MSYS2 UCRT64のbashで実行します．ビルドには時間がかかる場合があります．

```sh
git clone https://github.com/HoerTech-gGmbH/openMHA
cd openMHA
./configure --prefix=/ucrt64 && make install
mha '?' mhalib=identity cmd=quit
```

自分でビルドしたWindows版は，MSYS2 UCRT64のターミナルから起動してください．

### テストと既知の問題

Gitクローンのディレクトリ内のMSYS2 UCRT64シェルで実行します．

- lsl2acなど，ネットワーク通信を使うテストは，厳しいファイアウォールやネットワーク設定で失敗・停止する場合があります．訳注：この版ではlsl2acのソースは `disabled` 配下へ移動しています．
- MinGW UCRTツールチェーンとlibtorchは互換性がないため，Windowsではlibtorchを使うプラグインをビルドしません．

単体テストは次のとおりです．

```sh
make unit-tests
```

システムテストには，[Adoptium](https://adoptium.net)からWindows／JDK／MSIの64ビット版Temurinを導入し，インストーラーに `JAVA_HOME` を設定させます．さらに[Octave](https://octave.org)のWindows 64ビット版をインストールします．新しいMSYS2 UCRT64ターミナルで `openMHA/mha/mhatest` へ移動し，実際のOctaveパスに置き換えて起動します．

```sh
/<Path-to-Octave>/mingw64/bin/octave-cli
```

Octave内で実行します（関数名の綴りは原文どおりです）．

```matlab
set_environement; run_mha_tests
```

## IV. Linuxでドキュメントを再生成する

リリースには用途別のPDFマニュアルが含まれます．再生成する場合は，まずLinuxの通常ビルド用依存関係をインストールしてください．追加要件はUbuntu 22.04または26.04と，doxygen，fig2dev，graphviz，texlive，texlive-latex-extra，texlive-font-utilsです．

Ubuntu 26.04だけで実行します．

```sh
cp mha/doc/openMHAdoxygen-26.04.sty mha/doc/openMHAdoxygen.sty
```

両バージョン共通で実行します．

```sh
./configure && make doc
```

PDFはGitルートディレクトリへ，DoxygenのHTMLドキュメントは `mha/doc/mhadoc/html/` へ生成されます．
