# 05-frequency-shifting: 周波数シフト

> [English version](README.txt)

このディレクトリには、`fshift_hilbert` および `fshift` プラグインの使い方を実演する設定ファイルと入力音声ファイルが含まれています。

`fshift` と `fshift_hilbert` の主な違いは、`fshift` の方が高速ですが FFT ビン単位でしか周波数をシフトできないことです。

プラグインの一般的な説明については、openMHA_plugins.pdf マニュアルの対応するセクションを参照してください。

| 設定ファイル | 説明 |
|---|---|
| `fbc.cfg` | 440Hz の正弦波を 520Hz にシフトする実演 |
| `fbc_combination.cfg` | プリリリース版汎用補聴器設定で周波数シフターを使用する方法（フィードバック抑制に利用可能） |
| `fshift_hilbert_live.cfg` | `fshift_hilbert` のライブ I/O 設定での使用方法 |
| `fshift.cfg` | `fshift` プラグインの使用方法（より粗い周波数シフト） |
