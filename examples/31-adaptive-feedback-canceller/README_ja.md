# 31-adaptive-feedback-canceller: 適応フィードバックキャンセラ

> [English version](README.md)

適応フィードバックキャンセラ（AFC）の3種類のサンプルがあります。現在のプラグインは基本的な実装であり、無相関化の手段はフォワードパスの遅延のみです。調和信号（音声、音楽など）のような相関信号に対しては脆弱です。

**サンプル 2, 3 共通の JACK サーバー設定:**
- サンプルレート: 44100
- frames/period: 512
- オーディオデバイスの最初の入出力チャンネルを使用

## 1. デバッグ

AFC の基本的なデバッグ用サンプルです。各オーディオブロック処理後の変数状態を調べることができます。`run_afc_debug.m` を実行し、画面の指示に従ってください。比較用に、MATLAB のみの AFC 実装 `afc_standalone.m` も実行できます。

## 2. シミュレーション

JACK サーバー経由でリアルタイム実行しますが、出力を直接入力に送るため、ラウドスピーカーやマイクロフォンは不要です。JACK サーバーを起動し、`run_afc_sim.m` を実行してください。

## 3. ライブサンプル

実環境での AFC 使用方法を示します。アルゴリズム開始前にマイク-スピーカー系のキャリブレーションが必要です。

1. **キャリブレーション**: `get_calibration_level.m` を実行し、結果の値を `afc_live_example.cfg` の `mha.afc.gain.gains` に設定
2. **ラウンドトリップレイテンシ測定**: `jack_iodelay` を使用:
   - JACK サーバーを起動
   - `jack_iodelay` を起動
   - `jack_iodelay` の出力をデバイスの再生チャンネルに、デバイスの録音チャンネルを `jack_iodelay` の入力に接続
   - 「total roundtrip latency」の値（サンプル数、切り捨て）を `afc_live_example.cfg` の `mha.afc.measured_roundtrip_latency` に設定
   - `jack_iodelay` を停止
3. `run_afc_live_example.m` を実行

**注意事項:**
- CPU 負荷が高くなる場合があります。Linux ユーザーは lowlatency カーネルの使用を推奨
- 異常なノイズが発生した場合は、JACK サーバーの再起動で解決することがあります。再起動後はラウンドトリップレイテンシが変わる場合があるため、実測値より数サンプル小さい値を使用することを推奨
