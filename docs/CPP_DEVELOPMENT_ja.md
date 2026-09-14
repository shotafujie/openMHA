# C++中心の開発と検証

## 検証済みの基盤（2026-09-09）

MATLAB／Octaveは起動せず，C++のビルドと数値テストで検証しています．

- 上流4.18.1（`0b9f087e`）は前回，既存の和訳・Python拡張を保持してmasterへ統合済みです．
- README，インストール，ビルド，スタートガイド，聴覚損失シミュレーションの和訳を更新しました．NAL-NL2の和訳を追加しました．
- macOS 26.5.2／Apple Silicon／Apple Clang 21.0.0／C++17でビルドとローカルインストールが成功しました．
- `make -j6 unit-tests` は終了コード0，15個のテストランナーで計230件成功しました．
- C++組み込みサンプルとCLIファイル処理のCTestは3件成功しました．
- HSIMの既定ファイル処理もMATLABなしで終了コード0となり，48 kHz，2チャンネル，213915フレームのWAVが生成されました．聴覚モデルとしての妥当性や聴感は未検証です．

## 環境と再実行

今回追加したHomebrewパッケージは `jack liblo eigen boost labstreaminglayer/tap/lsl` です．libsndfile，portaudio，pkg-configは既存環境を使用しました．依存解決によりcmakeも更新されています．JACKの常駐サービスは開始していません．PyTorch依存の機能は `--with-torch=no` で除外しています．

リポジトリのルートで実行します．`.local` はGit管理対象外のインストール先です．

```sh
./configure --prefix="$PWD/.local" --with-torch=no
make -j6
make -j6 unit-tests
make install
export MHA_LIBRARY_PATH="$PWD/.local/lib"
export PATH="$PWD/.local/bin:$PATH"
mha '?' cmd=quit
cmake -S examples/cpp-embedding -B examples/cpp-embedding/build
cmake --build examples/cpp-embedding/build
ctest --test-dir examples/cpp-embedding/build --output-on-failure
```

上流の単体テスト準備処理はGoogleTestを取得・更新します．今回使用したGoogleTestのコミットは `4fed5f28` です．ログ中のLSL向け `library 'lsl' not found` は，既存Makefileが通常のライブラリリンクを試した後，macOSのframeworkリンクへフォールバックする際の出力です．最終的なビルド・テストは成功しています．

今回のバイナリは，和訳などの未コミット変更がある状態で作成した開発ビルド `4.18.1+` です．Gitコミット後に実行すると，コミット識別用オブジェクトが再ビルドされる場合があります．

## C++アプリからの呼び出し

[最小サンプル](../examples/cpp-embedding/main.cpp) は `libopenmha` をリンクし，`PluginLoader::mhapluginloader_t` で既存の `gain` プラグインをロードします．MATLAB，TCP制御，音声デバイスを必要としません．

処理の順序は，AC変数領域の作成 → プラグインのロード → 設定 → `prepare` → 音声ブロックごとの `process` → `release` です．AC領域はプラグインより長く生存させます．出力バッファの所有権は呼び出し元へ移りません．gainは入力を直接変更します．別のプラグインに変更する場合は，出力のチャンネル数・長さ・領域も確認する必要があります．

サンプルは48 kHz，128フレーム，ステレオの24ブロックを処理し，左右別の3種類のゲインと設定変更を検証します．基準式 `出力 = 入力 × 10^(dB/20)` に対する最大絶対誤差は `1.2335e-08` でした．範囲外のゲインも拒否されました．

[WAV検証プログラム](../examples/cpp-embedding/verify_gain_file.cpp) は既存の `examples/00-gain` をCLIで処理した出力を全サンプル比較します．152434ステレオフレーム，左右 `[-10 10] dB` に対する最大絶対誤差は `7.65172e-08` でした．CTestが入力例を読み，ビルドディレクトリに出力を生成するため，元の音声ファイルは変更しません．

## 2026-09-10の追加実装

[process_file](../examples/cpp-embedding/README_ja.md) を追加しました．C++アプリがlibsndfileで音声を読み，`mhachain` で複数の既存プラグインを接続してWAVを出力します．2段のゲインとローパスフィルターの設定例を用意し，ブロック境界・最終端数を含む全サンプル比較が成功しました．追加CTestは出力準備を含め9件です．既存出力の上書きを拒否することも確認しました．

翻訳は [一覧](TRANSLATIONS_ja.md) から辿れます．校正マニュアルは既存の翻訳を確認し，リリース手順，商用ルール，補助ツール，リファレンスアルゴリズムのREADMEの不足分を追加しました．既存訳すべての逐語的な再校閲まで完了したとはしていません．

2026-09-14に [校正付きコンプレッサの数値検証](COMPRESSOR_VALIDATION_ja.md) を追加しました．仮想の音圧校正，圧縮曲線，アタック／ディケイの収束，ブロックサイズ非依存性を検証し，CTest計10件が成功しています．実機を測定して校正したわけではありません．

次の拡張は，自前アプリの対象OSと音声入出力に合わせたホスト設計，実機校正，実時間処理の検証です．現在のCMakeとバイナリの実測確認はmacOSのみです．配布にはライブラリの配置・検索パスの設計も必要です．

実デバイスの入出力・遅延・ドロップアウト，MATLAB／Octaveの `make test`，PyTorch依存機能，Windows／Linuxでの動作は未検証です．リアルタイム化する際は，ブロックサイズ，バッファ所有権，制御スレッドと音声スレッドの分離を確認します．サンプルの設定変更は単一スレッドでブロック間に行っています．

コードの利用・改変・配布条件は [COPYING](../COPYING) のAGPLv3を確認します．特に非公開アプリへの組み込みや配布方式は，実装方法を決める段階で整理が必要です．今回，ライセンス適合性の最終判断はしていません．

## ログと生成物

ログはこのPCの `/tmp/openmha-build-20260909.log`，`/tmp/openmha-unit-tests-20260909.log`，`/tmp/openmha-install-20260909.log` にあります．手動実行の出力は `/tmp/openmha-gain-20260909.wav` と `/tmp/openmha-hsim-20260909.wav` です．`/tmp` は再起動などで失われる可能性があるため，主要な検証結果を上に記録しています．
