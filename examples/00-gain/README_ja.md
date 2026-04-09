# 00-gain: ゲイン適用の最小サンプル

> [English version](README.txt)

openMHA を使用した簡単なオーディオ処理タスク（ライブ処理とファイル間処理の両方）の最小限のサンプルです。

ここではオーディオ入力信号にゲインを適用する処理を実演しています。

| 設定ファイル | 説明 |
|---|---|
| `gain.cfg` | MHAIOFile プラグインを使用したファイル間処理 |
| `gain_live.cfg` | MHAIOJack プラグインを使用したライブ処理 |
| `gain_live_double.cfg` | JACK サーバーとオーディオ処理間のダブルバッファリングを使用したライブ処理 |

設定ファイルには詳細なコメントが記載されています。このサンプルの使い方は [openMHA スタートガイド](../../mha/doc/starting_guide/openMHA_starting_guide_ja.md) でステップバイステップで説明されています。
