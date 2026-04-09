# 17-PHL-generic-hearing-aid: 汎用補聴器設定

> [English version](README)

このディレクトリの設定ファイル `generic-hearing-aid` は、以下のプラグインを組み合わせています:

- キャリブレーション
- 適応型差動マイクロフォン
- STFT 処理
- コヒーレンスフィルタリング
- フィルタバンク
- ダイナミックコンプレッション
- ピッチシフター

これらを組み合わせることで、サンプル 4 と同様の汎用補聴器を構成しますが、ポータブルハードウェアでの使用に最適化されています。ダイナミックコンプレッサーのサンプル設定もいくつか提供されています。

`nodered/openMHAcontrol.flow` は node-red ベースの GUI 用のフローファイルを提供します。このフローには `node-red-dashboard` ノードが必要です。

## 使い方

```
mha ?read:generic-hearing-aid.cfg cmd=start
```

このサンプルは元々、Portable Hearing Laboratory（PHL）用の Mahalia オペレーティングシステムに含まれていたものです。他の環境で使用する場合は、設定ファイル内のパスの調整が必要になることがあります。
