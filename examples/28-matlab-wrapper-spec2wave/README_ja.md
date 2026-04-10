# 28-matlab-wrapper-spec2wave: MATLAB ラッパー（スペクトル→波形処理）

> [English version](README.txt)

このサンプルは、`matlab_wrapper` プラグインでスペクトル→波形処理のコードを書く方法を実演します。`process.m` に含まれる処理コードは、素朴なボコーダーを実装しています。

ユーザー設定可能な周波数ベクトルの各周波数 f について、まずオーディオブロックに正確にフィットする正弦波を生成する最近傍の周波数 f' に変更します。

次に、各周波数 f' に対して、スペクトル中の周波数 f に対応する周波数ビンの振幅に比例した振幅の正弦波を注入します。

実行するには MATLAB Coder が必要です。MATLAB で `make.m` を実行してライブラリを生成します。これにより C コードおよび（Coder 設定に応じて）共有ライブラリが生成されます。

共有ライブラリを openMHA プラグインディレクトリにコピーし、openMHA で `example_28.cfg` を実行してください。詳細は openMHA_matlab_coder_integration.pdf を参照してください。
