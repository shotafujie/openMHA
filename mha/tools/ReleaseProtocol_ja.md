# リリース手順

[原文](ReleaseProtocol.md)の日本語訳です．対応：上流 `0b9f087e`．ここに記載された手順は上流のリリース担当者向けです．このフォークで本手順を実行した，または正式なリリース検証を完了したことを意味しません．

## ブランチ方針

新しいリリースはdevelopmentブランチで準備します．リリース時にmasterをdevelopmentの状態へfast-forwardします．squash mergeは行いません．

## 環境

PDFマニュアルを生成できるUbuntu環境からのみリリースします．openMHAのビルド・ドキュメント生成に必要な環境と，動作するJACKをあらかじめ用意します．ヘッドホン，マイク，サウンドカードも必要です．

手動テストではJACKとALSAを使うMHAインスタンスが音声機器にアクセスします．画面共有付きビデオ通話も音声機器を使うため，同時実行は難しいと考えられます．

## 手順

1. 変更のない新しいworktreeを作成します．
2. `./configure --prefix=<標準外の任意のインストール先>` を実行します．
3. `make test unit-tests` を実行します．
4. 以下の手動テストを実施します．
5. `make release` を実行します．
6. ニュースリリースを公開します．

## 手動のリリース前テスト

以下のテストはLinuxで実行し，JACKとaudioグループへのユーザー登録が必要です．

### test_mhaioalsa.mなどの自動ライブテスト

ALSAループバックモジュール，aplay，arecordを用意します．原文の設定コマンドは次のとおりです．システム設定を変更するコマンドなので，対象のテスト機で実施します．

```sh
sudo apt-get install alsa-utils
grep snd-aloop /etc/modules || echo snd-aloop | sudo tee -a /etc/modules
grep "alias snd-card 0 snd-aloop" /etc/snd-aloop.conf || (echo "alias snd-card 0 snd-aloop"; echo "options snd-aloop index=0 pcm_substreams=2") | sudo tee -a /etc/snd-aloop.conf
```

続けてOctaveまたはMATLABで実行します．

```sh
cd mha/mhatest
octave --no-gui --no-window-system --eval "set_environment;global execute_live_tests=true;exit(~run_mha_tests())"
```

または同じディレクトリで実行します．

```sh
matlab -nodesktop -nosplash -nodisplay -r"set_environment;global execute_live_tests=true;exit(~run_mha_tests())"
```

ALSAループバックが未導入の場合，テスト全体が成功に見えてもMHAIOalsaの検査がスキップされるため，合格とは扱いません．この場合は `warning: ALSA Loopback device is not available, can not test ALSA IO` と表示されます．`sudo modprobe snd-aloop` でモジュールをロードします．

### gain_liveとダイナミックコンプレッサのライブ例

Gitルートへ戻って `make install` を実行し，新しいprefixのbinをPATHへ，libをLD_LIBRARY_PATHへ追加します．両方ともJACKの周期サイズは64の倍数，サンプルレートは44100 Hz，ハードウェアは2入力・2出力，マイクとヘッドホンを使用します．

gain_liveを起動します．

```sh
mha '?read:examples/00-gain/gain_live.cfg' cmd=start --interactive
```

初期状態では左が右より小さく聞こえるはずです．`mha.gain.gains=[-10 -10]` に変更すると左右同じ大きさになり，`mha.gain.gains=[10 10]` に変更すると左右とも同じだけ大きくなります．

ダイナミックコンプレッサを起動します．

```sh
mha '?read:examples/01-dynamic-compression/example_dc_live.cfg' cmd=start --interactive
```

訳注：この設定ファイル名は原文どおりです．現在の配置と整合するか，実行前に確認してください．

初期利得表はほぼ減衰させるため，ほとんど聞こえないはずです．次の設定に変更します．

```text
mha.overlapadd.mhachain.dc.gtdata = [[60 20 -20];[60 20 -20];[60 20 -20];[60 20 -20]]
```

全周波数帯域で圧縮され，出力レベルが一定になることを確認します．MATLABのフィッティングGUIを起動し，異なる2つの処方ルールと微調整を試します．期待どおり変化することを確認してください．帯域数が少ないため，一部の微調整周波数では変化しません．

### オフラインフィッティングGUI

音声ファイルと可変圧縮率の処方ルールを用いて，オフラインGUIを検証します．

### 追加の手動テスト

ビルドツールを備えたWindowsデスクトップ機でopenMHAをビルドします．`openMHA/mha/mhatest/test_mhaioportaudio.m` は，音声機器のないWindowsビルドサーバーで想定されるInternal PortAudio errorを無視しています．この無視処理を外し，音声機器のあるWindows機でテストが成功することを確認してください．
