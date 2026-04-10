# 23-matlab-coder: MATLAB Coder による openMHA プラグイン生成

> [English version](README)

このサンプルは、MATLAB Coder を使用して openMHA をネイティブコンパイルし、openMHA プラグインを生成する方法を紹介します。MATLAB で実装された2チャンネル切替アルゴリズムを使用して、プラグイン生成のステップバイステップガイドを提供します。

## ファイル一覧

| ファイル | 説明 |
|---|---|
| `channel_switch.m` | プラグイン実装用のサンプルアルゴリズム |
| `make.m` | C コード生成用の MATLAB Coder スクリプト |
| `process.m` | C コードが生成されるユーザー関数 |
| `verification.m` | MATLAB と openMHA の出力が一致するか検証 |
| `plugin_skeleton/matlabcoder_skeleton.cpp` | プラグインスケルトンファイル |
| `plugin_skeleton/Makefile` | openMHA コンパイル用 Makefile |

## プラグインのコンパイル手順

1. MATLAB で実装したアルゴリズムを `process` 関数内に配置
2. `process` 関数はブロックを入力として受け取り、同サイズのブロックを出力する
3. `make.m` を実行して `process` 関数の C コードを生成（MATLAB Coder が必要）
4. `make.m` の実行でサブディレクトリ `codegen` が生成される
5. `codegen/lib/process/` を `mha/plugins/<PLUGIN_NAME>` ディレクトリにコピー
6. `plugin_skeleton/` 内のファイルも同じ `<PLUGIN_NAME>` ディレクトリにコピー
7. `matlabcoder_skeleton.cpp` を `<PLUGIN_NAME>.cpp` にリネーム
8. `make install` でコンパイルしてインストール

## 検証

- 検証ツールは MATLAB を使用します。MATLAB ツールの MHA 設定方法はアプリケーションマニュアルのセクション4を参照
- `verification.m` と `process.m`（および依存ファイル）を `mha/plugins/<PLUGIN_NAME>` ディレクトリに配置
- 検証関数は3つの引数を取ります: `<PLUGIN_NAME>`、テスト信号、フラグメントサイズ
- エラーが表示されなければ、出力は誤差マージン 10e-5 以内で一致しています
