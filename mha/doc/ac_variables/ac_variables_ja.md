# AC 変数の操作

> [English version (LaTeX)](ac_variables.tex)

## セットアップ

1. 実行中のすべての **MHA プロセスを終了**します
2. **MATLAB または Octave を起動**します
3. コマンドウィンドウで LD_LIBRARY_PATH を空に設定します:
   ```matlab
   setenv('LD_LIBRARY_PATH','')
   ```
4. MATLAB/Octave の「Current Folder」で以下のディレクトリに移動します:
   - **Linux**: `/usr/share/openmha/examples/05-frequency-shifting`
   - **Windows**: `C:\Program Files\openMHA\examples\05-frequency-shifting`
   - **macOS**: `/usr/local/share/openmha/examples/05-frequency-shifting`

5. openMHA の MATLAB 関数を使用するために、コマンドウィンドウで以下を入力:
   - **Linux**: `addpath('/usr/lib/openmha/mfiles')`
   - **Windows**: `addpath('C:\Program Files\openMHA\mfiles')`
   - **macOS**: `addpath('/usr/local/lib/openmha/mfiles/')`

6. 新しい openMHA インスタンスを起動:
   ```matlab
   openmha = mha_start;
   ```

7. 設定ファイルを読み込み:
   ```matlab
   mha_query(openmha,'','read:coherence_live.cfg');
   ```

8. **JACK サーバーを起動**（設定: サンプルレート = 44100, Frames/Period = 64）

9. MHA プロセスを開始:
   ```matlab
   mha_set(openmha, 'cmd', 'start');
   ```

10. **JACK Control**: サウンドカードの「capture」「playback」チャンネルを MHA の「in」「out」チャンネルに接続。マイクロフォンをサウンドカードに接続。

11. AC 変数を確認:
    ```matlab
    mha_get(openmha,'','mha.overlapadd.mhachain.acmon')
    mha_get(openmha,'','mha.overlapadd.mhachain.acmon.coherence_rcoh')
    ```

## 設定ファイルの例 (Gain_live.cfg)

```
# 処理するチャンネル数
nchannels_in = 2
# 各ブロックで処理するフレーム数
fragsize = 64
# サンプルレート（JACK の入力信号と同じにする必要がある）
srate = 44100
# transducers プラグインを使用
mhalib = transducers
# gain プラグインのみ使用
mha.algos=[ gain ]
# ゲインファクタの最大・最小値（dB）
mha.gain.min=-20
mha.gain.max=20
# 2つのゲインファクタ（左右）
mha.gain.gains=[ -10 10 ]
# JACK オーディオサーバーに接続する IO ライブラリ
iolib = MHAIOJackdb

mha.plugin_name = overlapadd

mha.calib_in.peaklevel = [90 90]
mha.calib_out.peaklevel = [90 90]

mha.overlapadd.fftlen = 256
mha.overlapadd.wnd.len = 128
```

## MATLAB スクリプトの例

```
# 処理するチャンネル数
nchannels_in = 2
# 各ブロックで処理するフレーム数
fragsize = 64
# サンプルレート（JACK の入力信号と同じにする必要がある）
srate = 44100
# mhachain プラグインを使用
mhalib = mhachain
# gain プラグインのみ使用
mha.algos=[ gain ]
# ゲインファクタの最大・最小値（dB）
mha.gain.min=-20
mha.gain.max=20
# 2つのゲインファクタ（左右）
mha.gain.gains=[ -10 10 ]
# JACK オーディオサーバーに接続する IO ライブラリ
iolib = MHAIOJackdb
```
