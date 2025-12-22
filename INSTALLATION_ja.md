# インストールガイド

このガイドでは、Linux（**I.**）、macOS（**II.**）、Windows（**III.**）オペレーティングシステムでのopenMHAのインストール手順を説明します。

**[English version is here / 英語版はこちら](INSTALLATION.md)**

**[READMEに戻る](README_ja.md)**

---

## 目次

- [I. Linuxでのバイナリパッケージからのインストール](#i-linuxでのバイナリパッケージからのインストール)
- [II. macOSでのHomebrewによるインストール](#ii-macosでのhomebrewによるインストール)
- [III. Windowsインストーラ](#iii-windowsインストーラ)

---

## I. Linuxでのバイナリパッケージからのインストール

### Ubuntu および ARMベースLinuxシステム向け

まず、openMHAパッケージリポジトリをシステムに追加します：

**Ubuntu 24.04の場合：**

```bash
wget -qO- http://apt.hoertech.de/openmha-packaging.pub | sudo tee /etc/apt/trusted.gpg.d/openmha-packaging.asc
sudo apt-add-repository 'deb [arch=amd64] http://apt.hoertech.de noble universe'
```

**Ubuntu 22.04の場合：**

```bash
wget -qO- http://apt.hoertech.de/openmha-packaging.pub | sudo tee /etc/apt/trusted.gpg.d/openmha-packaging.asc
sudo apt-add-repository 'deb [arch=amd64] http://apt.hoertech.de jammy universe'
```

**Ubuntu 20.04の場合：**

```bash
wget -qO- http://apt.hoertech.de/openmha-packaging.pub | sudo apt-key add -
sudo apt-add-repository 'deb [arch=amd64] http://apt.hoertech.de focal universe'
```

**ARM CPUを搭載したコンピュータ（Debian、Ubuntu、Raspberry Pi OS、Armbianなどの派生版を実行）の場合：**

以下の手順は32ビットおよび64ビットARMシステムの両方で動作します。32ビットARMシステムの要件として、CPUは少なくともARMv7である必要があります。

Debian 10またはUbuntu 20.04ベースのARMシステムの場合：

```bash
wget -qO- http://apt.hoertech.de/openmha-packaging.pub | sudo apt-key add -
echo 'deb http://apt.hoertech.de bionic universe' | sudo tee /etc/apt/sources.list.d/openmha.list
sudo apt update
```

Debian 11またはUbuntu 22.04以降ベースのARMシステムの場合：

```bash
wget -qO- http://apt.hoertech.de/openmha-packaging.pub | sudo tee /etc/apt/trusted.gpg.d/openmha-packaging.asc
echo 'deb http://apt.hoertech.de bullseye universe' | sudo tee /etc/apt/sources.list.d/openmha.list
sudo apt update
```

### openMHAのインストール

openMHAといくつかの使用例をインストールします：

```bash
sudo apt install openmha openmha-examples
```

インストール後、openMHAのドキュメントは `/usr/share/doc/openmha` に、GNU Octave/Matlab用ツールは `/usr/lib/openmha/mfiles` にあります。

openmha-examplesパッケージをインストールすると、サンプルは `/usr/share/openmha/examples` にあります。

リファレンスアルゴリズムは `/usr/share/openmha/reference_algorithms` にあります。

**注意：** サンプルファイルを使用する場合は、ホームディレクトリにコピーを作成することをお勧めします。これらはシステム全体の読み取り専用ディレクトリにあり、一部のサンプルは現在のオーディオハードウェア設定で動作させるために変更が必要で、出力を保存するための書き込みアクセスが必要な場合があります。

独自のプラグインを実装したいアルゴリズム開発者は、開発パッケージ **libopenmha-dev** もインストールする必要があります。

### openMHAの更新

新しいリリースが利用可能になったときにopenMHAを更新するには、以下を実行します：

```bash
sudo apt update
sudo apt install openmha
```

これにより、インストールされているすべてのopenmhaパッケージが最新バージョンにアップグレードされます。

---

## II. macOSでのHomebrewによるインストール

（注意：古いバージョンのopenMHA（4.17.0以前）をアップグレードする場合、以前はpkgインストーラを使用していたため、まず古いバージョンを削除する必要があります。次のセクション「macOSでのopenMHAのアンインストール」を参照してください。）

Homebrewをインストールして更新します。手順は https://brew.sh にあります。

以下のコマンドでopenMHAをインストールします：

```bash
brew install openmha/tap/openmha
```

openMHAはインストール中にいくつかのテストを実行します。インストールプロセス中にネットワークアクセスなどの許可を求められる場合があります。

（注意：いくつかのHomebrewパッケージがリンクできなかったためにインストールが失敗した場合、openMHAまたはその依存関係の古い非Homebrewバージョンがインストールされています。それらをアンインストールして再試行してください。次のセクション「macOSでのopenMHAのアンインストール」も参照してください。）

Homebrewはopenのサンプル設定といくつかのツールをインストールします。サンプルフォルダをユーザーディレクトリ内の書き込み可能な場所にコピーすることをお勧めします。

### インストール場所

デフォルトのインストール場所はMacのプロセッサタイプによって異なります：

**Intel CPUを搭載したMacの場合：**
- サンプルフォルダ：`/usr/local/share/openmha/examples/`
- リファレンスアルゴリズム：`/usr/local/share/openmha/reference_algorithms`
- MatlabまたはOctave用mファイル：`/usr/local/lib/openmha/mfiles/`
- ドキュメント：`/usr/local/share/doc/openmha/`

**ARMプロセッサ（Apple Silicon）を搭載したMacの場合：**
- サンプルフォルダ：`/opt/homebrew/share/openmha/examples/`
- リファレンスアルゴリズム：`/opt/homebrew/share/openmha/reference_algorithms`
- MatlabまたはOctave用mファイル：`/opt/homebrew/lib/openmha/mfiles/`
- ドキュメント：`/opt/homebrew/share/doc/openmha/`

### II.a macOSでのopenMHAのアンインストール

openMHA v4.17.0以前がMacにインストールされている場合、Homebrewで新しいバージョンをインストールする前に、それとその依存関係をアンインストールする必要があります。スクリプト [Mac_Uninstall_openMHA_Jack_pkg](Mac_Uninstall_openMHA_Jack_pkg) を使用して、古いpkgインストーラでインストールされたopenMHAとJackをアンインストールできます。ファイルをダウンロードしてbashで実行します：

```bash
bash Mac_Uninstall_openMHA_Jack_pkg
```

Homebrewでopenインストールした場合は、以下のコマンドでアンインストールできます：

```bash
brew uninstall openmha
```

アップグレード前にHomebrew経由でインストールしたopenMHAをアンインストールする必要はありません。この場合、以下のコマンドで新しいバージョンにアップグレードできます：

```bash
brew update && brew upgrade
```

---

## III. Windowsインストーラ

64ビットWindows 10用のopenMHAインストーラは、GitHubリリースページからダウンロードできます：
https://github.com/HoerTech-gGmbH/openMHA/releases

インストーラはopenMHAのサンプル設定といくつかのツールをインストールします。サンプルフォルダをユーザーディレクトリ内の書き込み可能な場所にコピーすることをお勧めします。

### インストール場所

インストール後、以下の場所にファイルがあります：

- サンプル：`C:\Program Files\openMHA\examples`
- リファレンスアルゴリズム：`C:\Program Files\openMHA\reference_algorithms`
- Matlab/Octave用ファイル：`C:\Program Files\openMHA\mfiles`
- ドキュメント：`C:\Program Files\openMHA\doc`

### Jackオーディオ接続キット

互換性の問題により、WindowsビルドにはJackバージョン1.9.21が必要です。以下からダウンロードできます：
https://jackaudio.org/downloads/

---

## 関連ドキュメント

- [README（日本語）](README_ja.md)
- [コンパイルガイド（日本語）](COMPILATION_ja.md)
- [README (English)](README.md)
- [Compilation Guide (English)](COMPILATION.md)
