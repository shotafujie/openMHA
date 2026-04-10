# 09-localizer-steering-beamformer: 音源定位ステアリングビームフォーマ

> [English version](README.txt)

このディレクトリには、4つの補聴器マイクロフォンで収音した音の到来方向を推定し、定位された（コヒーレントな）音源の最も可能性の高い方向にビームフォーマアルゴリズムを制御する openMHA セットアップが含まれています。GCC-PHAT に基づく音源定位アルゴリズムの実装を使用しています（詳細は参考文献 [0], [1] および設定ファイルを参照）。

信号処理はシェルスクリプトを実行して開始できます:

```
start_demo_live_binauralSteerBF.sh
```

この例に向けた Jack サーバーの準備方法については、シェルスクリプト内のコメントも参照してください。

アルゴリズムの出力を可視化する場合は、別途ツールが [2] で利用可能です。（*注*: これは openMHA バージョン 4.9.0 から 4.11.0 では `visualisation_web/` サブディレクトリに含まれていました。）

## 参考文献

- [0] C. Knapp and G. C. Carter, "The generalized correlation method for estimation of time delay," IEEE Trans. Acoustics, Speech and Signal Processing, vol. 24, no. 4, pp. 320-327, Aug. 1976.
- [1] H. Kayser and J. Anemüller, "A discriminative learning approach to probabilistic acoustic source localization," In: IWAENC 2014, pp. 100-104, Antibes, France, 2014.
- [2] https://github.com/HoerTech-gGmbH/doasvm-visualizer
