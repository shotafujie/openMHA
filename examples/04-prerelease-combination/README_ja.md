# 04-prerelease-combination: プリリリースアルゴリズムの組み合わせ

> [English version](README.txt)

このディレクトリの設定ファイル `prerelease_combination.cfg` は、キャリブレーション、適応差動マイクロフォン、STFT処理、コヒーレンスフィルタリング、フィルタバンク、ダイナミックコンプレッションのプラグインを組み合わせています。

設定ファイルには詳細なコメントが記載されています。このアルゴリズムの組み合わせの詳細については、設定ファイル内のコメントを参照してください。

この設定はオーディオファイル処理を行います。このディレクトリ内の音声ファイル `1speaker_diffNoise_4ch.wav` を処理し、出力音声ファイル `1speaker_diffNoise_4ch_OUT.wav` を生成します。

処理は次のように開始します:

```
mha ?read:prerelease_combination.cfg cmd=start cmd=quit
```
