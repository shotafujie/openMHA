# 21-compile: 自作プラグインのコンパイル

> [English version](README.md)

openMHA のプラグイン開発ガイド（http://www.openmha.org/documentation/ からリンク）には、C++ で openMHA プラグインを書くチュートリアルが含まれています。C++ コードは openMHA で使用する前にコンパイルする必要があります。ソースコードからプラグインをコンパイルする方法をこの README で説明します。

このディレクトリには、サンプルプラグインのソースコード `example21.cpp` と、プラグインのコンパイルに使用できる `Makefile` が含まれています。

## Linux および macOS でのコンパイル

1. [INSTALLATION.md](../../INSTALLATION_ja.md) の説明に従って openMHA をインストールします（Linux の場合は `libopenmha-dev` パッケージも含めて）。

2. `example21.cpp` と `Makefile` が含まれるディレクトリで以下を実行:
   ```
   make
   ```

3. 生成されたライブラリファイルをグローバルライブラリディレクトリにコピー:

   **Linux:**
   ```
   sudo cp example21.so /usr/lib
   ```
   **macOS:**
   ```
   sudo cp example21.dylib /usr/local/lib
   ```

### PHL（Portable Hearing Laboratory）でのコンパイル

[examples/33-compile-plugin-on-PHL](../33-compile-plugin-on-PHL/README_ja.md) の README を参照してください。

## Windows でのコンパイル

1. [INSTALLATION.md](../../INSTALLATION_ja.md) の説明に従って openMHA をインストール。

2. [COMPILATION.md](../../COMPILATION_ja.md) の説明に従って Windows 用ビルド環境をインストール。インストールした GCC コンパイラのバージョンが `C:\Program Files\openMHA\config.mk` に記載のバージョンと一致していることを確認。

3. openMHA ヘッダファイルを取得するため、Git で openMHA ソースコードをクローン。

4. このディレクトリの Makefile を編集:
   - include 行を変更: `include /c/Progra~1/openMHA/config.mk`
   - LIBS 設定を拡張: `LIBS = -L/c/Progra~1/openMHA/bin -lopenmha`
   - INCLUDES 設定を変更: 手順3でクローンした openMHA ディレクトリ内の `mha/libmha/src` を参照

5. MinGW64 bash シェルで以下を実行:
   ```
   make
   ```

6. 生成された `*.dll` ファイルを `C:\Program Files\openMHA\bin` にコピー。

## 自作プラグインの使用

openMHA 設定で、自作プラグインを他のプラグインと同様に読み込みます。ここでコンパイルしたサンプルプラグインは、設定内で拡張子なしのファイル名「example21」として参照されます。
