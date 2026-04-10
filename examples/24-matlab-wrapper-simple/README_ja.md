# 24-matlab-wrapper-simple: MATLAB ラッパー（シンプル版）

> [English version](README.txt)

このサンプルは、`matlab_wrapper` プラグインで波形→波形処理のコードを書く方法を実演します。`process.m` に含まれる処理コードは、ステレオ信号の左右チャンネルを入れ替えます。

実行するには MATLAB Coder が必要です。MATLAB で `make.m` を実行してライブラリを生成します。これにより C コードおよび（Coder 設定に応じて）共有ライブラリが生成されます。

共有ライブラリを openMHA プラグインディレクトリにコピーし、openMHA で `example_24.cfg` を実行してください。詳細は openMHA_matlab_coder_integration.pdf を参照してください。
