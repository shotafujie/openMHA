# インストール手順

[英語原文](INSTALLATION.md)／対応：openMHA 4.18.1（上流 `0b9f087e`）．

Linux，macOS，Windowsへのインストール方法を説明します．ソースコードからビルドする場合は [COMPILATION_ja.md](COMPILATION_ja.md) を参照してください．

## I. Ubuntuへのインストール

[GitHubのリリースページ](https://github.com/HoerTech-gGmbH/openMHA/releases)から最新版を探してください．UbuntuのバージョンとCPUアーキテクチャに応じたZIPファイルが提供されています．対応するZIPをダウンロードして展開し，含まれる `openmha-packages` ディレクトリをターミナルで開いて実行します．

```sh
sudo apt install ./*.deb
```

インストール後の配置先は次のとおりです．

| 内容 | 場所 |
| --- | --- |
| ドキュメント | `/usr/share/doc/openmha` |
| GNU Octave／MATLAB用ツール | `/usr/lib/openmha/mfiles` |
| 使用例（openmha-examplesパッケージ） | `/usr/share/openmha/examples` |
| リファレンスアルゴリズム | `/usr/share/openmha/reference_algorithms` |

使用例はシステム全体の読み取り専用ディレクトリにあるため，ホームディレクトリ内へコピーして使うことを推奨します．使用するオーディオ機器に応じた設定変更や，出力保存のための書き込み権限が必要な例があります．

## II. HomebrewによるmacOSへのインストール

[Homebrew](https://brew.sh)の手順に従ってHomebrewをインストール・更新し，次を実行します．

```sh
brew install openmha/tap/openmha
```

インストール中にテストを実行するため，ネットワークアクセスなどの許可を求められる場合があります．使用例とツールもインストールされます．使用例フォルダをユーザーディレクトリ内の書き込み可能な場所へコピーすることを推奨します．標準の配置先はCPUによって異なります．

| 内容 | Intel Mac | Apple Silicon Mac |
| --- | --- | --- |
| 使用例 | `/usr/local/share/openmha/examples/` | `/opt/homebrew/share/openmha/examples/` |
| リファレンスアルゴリズム | `/usr/local/share/openmha/reference_algorithms` | `/opt/homebrew/share/openmha/reference_algorithms` |
| MATLAB／Octave用mファイル | `/usr/local/lib/openmha/mfiles/` | `/opt/homebrew/lib/openmha/mfiles/` |
| ドキュメント | `/usr/local/share/doc/openmha/` | `/opt/homebrew/share/doc/openmha/` |

## III. Windowsへのインストール

[GitHubのリリースページ](https://github.com/HoerTech-gGmbH/openMHA/releases)から最新版を探してください．x64用とARM64用のZIPが提供されています．対応するZIPをダウンロードし，`C:\Program Files` など任意の場所へ展開します．ZIP内の `openMHA` フォルダに，インストールに必要な全ファイルが含まれています．システムのPATH環境変数に `C:\Program Files\openMHA\bin` を追加してください．別の場所へ展開した場合は，その場所に合わせてください．

| 内容 | 標準の展開先を使用した場合 |
| --- | --- |
| 使用例 | `C:\Program Files\openMHA\examples` |
| リファレンスアルゴリズム | `C:\Program Files\openMHA\reference_algorithms` |
| MATLAB／Octave用ファイル | `C:\Program Files\openMHA\mfiles` |
| ドキュメント | `C:\Program Files\openMHA\doc` |
