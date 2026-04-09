# 01-dynamic-compression: ダイナミックレンジコンプレッション

> [English version](README.txt)

openMHA を使用してオーディオ入力にダイナミックレンジコンプレッションを適用する最小限のサンプルです。

| 設定ファイル | 説明 |
|---|---|
| `dynamiccompression.cfg` | MHAIOFile プラグインを使用したファイル間処理 |
| `dynamiccompression_live.cfg` | MHAIOJack プラグインを使用したライブ処理 |
| `example_dc_live.cfg` | ライブ処理の別の設定例 |
| `example_dc_live_double.cfg` | JACK サーバーとオーディオ処理間のダブルバッファリングを使用したライブ処理 |

設定ファイルには詳細なコメントが記載されています。openMHA の起動方法とオーディオ処理のセットアップについては、[openMHA スタートガイド](../../mha/doc/starting_guide/openMHA_starting_guide_ja.md) と [プラグインマニュアル](http://www.openmha.org/docs/openMHA_plugins.pdf) を参照してください。
