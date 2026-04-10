# 30-marker-streams: マーカーストリーム

> [English version](README)

このサンプルは、`lsl2ac` プラグインを使用してマーカーストリームを受信する方法を実演します。3つのファイルで構成されています:

| ファイル | 説明 |
|---|---|
| `Makefile` | `SendStringMarkers.cpp` をコンパイルするため |
| `SendStringMarkers.cpp` | 「MyEventStream」という名前の LSL ストリーム経由でネットワークに文字列マーカーを送信 |
| `string_markers.cfg` | openMHA 設定ファイル |

## 実行方法

まず `SendStringMarkers` をコンパイルします:

```
make SendStringMarkers
```

次に `SendStringMarkers` を起動し、別のシェルで MHA を起動して受信値を確認します:

```
./SendStringMarkers
```

```
mha ?read:string_markers.cfg --interactive cmd=start
mha.acmon.MyEventStream?val
```
