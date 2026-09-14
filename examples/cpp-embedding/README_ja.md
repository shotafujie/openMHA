# MATLABを使わないC++組み込み例

macOSで検証した，既存プラグインを直接利用するオフラインC++アプリです．`libopenmha` とプラグインを同一プロセスにロードします．音声デバイスやJACKサーバー，MATLAB，TCP制御は不要です．ビルド環境は [C++開発ガイド](../../docs/CPP_DEVELOPMENT_ja.md) を参照してください．

## ビルド・検証

リポジトリのルートで実行します．openMHAを先に `.local` へインストールしてください．

```sh
cmake -S examples/cpp-embedding -B examples/cpp-embedding/build
cmake --build examples/cpp-embedding/build
ctest --test-dir examples/cpp-embedding/build --output-on-failure
```

別のインストール先を使う場合は，CMakeに `-DOPENMHA_ROOT=/absolute/path/to/prefix` を指定します．

## 自分のWAVを処理する

ルートディレクトリから，入力と新しい出力のパスを指定します．

```sh
export MHA_LIBRARY_PATH="$PWD/.local/lib"
examples/cpp-embedding/build/process_file \
  examples/00-gain/1speaker_diffNoise_2ch.wav \
  /tmp/my-openmha-output.wav \
  examples/cpp-embedding/gain-chain.cfg
```

出力が既に存在する場合は上書きせず失敗します．別の出力名を指定してください．実行途中の失敗で新しい出力が残った場合，そのファイルは未完成の可能性があります．

[gain-chain.cfg](gain-chain.cfg) は2つのgainプラグインを接続し，左右の最終ゲインを `[-10 10] dB` にします．[lowpass-chain.cfg](lowpass-chain.cfg) に替えると，-6 dBのゲインと2サンプル移動平均フィルターを適用します．設定は `mhachain` の内部を記述するため，CLI用設定の `mhalib` や `mha.` 接頭辞は不要です．IIR係数の変数名は大文字の `A` と `B` です．

[compressor-chain.cfg](compressor-chain.cfg) では `transducers` がWAVの振幅をPaへ換算し，`dc_simple` で圧縮してから出力振幅へ戻します．使い方は同じで，最後の引数をこの設定ファイルに替えます．左右の校正値は検証用の仮定であり，測定済みの機器設定ではありません．詳細は [コンプレッサ検証](../../docs/COMPRESSOR_VALIDATION_ja.md) を参照してください．

## コードの読み方

| ファイル | 役割 |
| --- | --- |
| [main.cpp](main.cpp) | gainのロード，設定変更，128フレームごとの処理，数値検証 |
| [process_file.cpp](process_file.cpp) | libsndfileでWAVを読み，mhachainへバッファを渡して出力 |
| [verify_gain_file.cpp](verify_gain_file.cpp) | 既知のゲイン／フィルター式による全サンプルの比較 |
| [verify_compressor.cpp](verify_compressor.cpp) | 圧縮曲線，校正換算，動的応答，ブロックサイズ非依存性の検証 |

`Chain` のAC領域はプラグインより先に作り，後で破棄します．`prepare` 後に `process` を呼び，終了時に `release` します．出力バッファは借用です．コピーせず所有権を移したり，手動解放したりしないでください．

## 現在の範囲

入出力は同じチャンネル数・サンプルレート・フレーム数の時間領域信号に限定しています．最後の128フレーム未満のブロックはゼロで埋め，元の長さの分だけ保存します．出力は32ビット浮動小数点WAVで，ピークを表示します．±1を超える値も保存できるため，再生側でクリップしないレベルを設定してください．

フィルターの残響末尾は書き出さず，アルゴリズム遅延の補償も行いません．サンプルレート変換，スペクトル入出力，実時間のデバイス処理向けホストではありません．音圧校正が必要なコンプレッサへ拡張するときは，正規化WAV振幅とPaの対応を設定する必要があります．

10件のCTestは単体gain，CLIによるWAV処理，自前ホストによる2段gainとローパス，各出力の数値比較，既存出力の上書き拒否，出力準備，校正付きコンプレッサを含みます．ローパスの比較はブロック境界をまたぐフィルター状態と，最終端数ブロックも検査します．テストはビルドディレクトリ内の `gain-chain.wav` と `lowpass-chain.wav` を再生成します．

ソースはAGPLv3です．配布・他アプリへの組み込み時は [COPYING](../../COPYING) の条件を確認してください．
