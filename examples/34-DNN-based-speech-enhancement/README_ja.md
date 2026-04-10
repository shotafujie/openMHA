# 34-DNN-based-speech-enhancement: DNN ベース音声強調

> [English version](README.txt)

このサンプルは、openMHA で実装されたリアルタイム動作する各種補聴器信号強調アルゴリズムを実演します。

## 利用可能な手法

**古典的空間フィルタリング（2種）:**
- 両耳適応差動マイクロフォン（ADM）
- 両耳最小分散無歪応答（MVDR）ビームフォーマ

**ディープニューラルネットワーク（DNN）ベースのアプローチ（3種）:**
- 単耳グループ通信フィルタ加算ネットワーク（GCFSnet_mono）
- 両耳グループ通信フィルタ加算ネットワーク（GCFSnet_bin）
- 両耳マルチフレームウィーナーフィルタ（bMFWF）

両耳の耳掛け型（BTE）補聴器セットアップを想定し、各耳に2つのマイクロフォン（10mm 間隔）を使用します（Portable Hearing Lab で利用可能な耳レベルデバイスなど。http://www.openmha.org/hardware/ 参照）。

## 実行方法

JACK サーバーを起動します（4入力チャンネル、2出力チャンネル、サンプルレート 48000 Hz、96 frames/period）。

次のコマンドを実行:

```
export OMP_NUM_THREADS=1; mha '?read:index.cfg'
```

（`OMP_NUM_THREADS=1` はマルチスレッドのオーバーヘッドによるシステム過負荷を防ぐために実行コア数を1に制限しています。）

実行時にアルゴリズムを切り替えることができます:

```
mha.transducers.mhachain.signal_enhancement.select = {pass ADM MVDR GCFSnet_mono GCFSnet_bin bMFWF}
```

`pass` がデフォルト設定で、信号強調を適用しません。

## DNN ベースアルゴリズムに関する注意

- これらは openMHA でディープラーニングベースの音声強調をリアルタイム・低遅延で実行する能力を実演するための実験的アルゴリズムです
- 絶対音圧レベルに敏感なため、適切に動作するには校正済みセットアップが必要です。`index.cfg`（9-10行目）のキャリブレーションパラメータを調整してください
- CPU 負荷が高くなる場合があります。特に bMFWF は高い処理性能を必要とし、一部のコンピュータでは正常に動作しない場合があります
