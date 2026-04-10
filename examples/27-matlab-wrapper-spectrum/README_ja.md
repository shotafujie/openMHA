# 27-matlab-wrapper-spectrum: MATLAB ラッパー（スペクトル処理）

> [English version](README.txt)

このサンプルは、`matlab_wrapper` プラグインでスペクトル→スペクトル処理のコードを書く方法を実演します。`process.m` に含まれる処理コードは、スペクトル領域での汎用フィルタを実装しています。フィルタ係数は FFT ビンと要素ごとに乗算されます。有効な設定にするには、FFT ビン数と同数のフィルタ係数が必要です。

実行するには MATLAB Coder が必要です。MATLAB で `make.m` を実行してライブラリを生成します。これにより C コードおよび（Coder 設定に応じて）共有ライブラリが生成されます。

共有ライブラリを openMHA プラグインディレクトリにコピーし、openMHA で `example_27.cfg` を実行してください。詳細は openMHA_matlab_coder_integration.pdf を参照してください。
