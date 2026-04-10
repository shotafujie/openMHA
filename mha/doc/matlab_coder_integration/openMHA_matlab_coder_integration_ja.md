# MATLAB Coder 統合

> [English version (LaTeX)](openMHA_matlab_coder_integration.tex)

## はじめに

多くの聴覚研究者にとって、新しいアルゴリズムのプロトタイピングに最適なツールは MATLAB です。プロトタイプが一定の成熟度に達すると、準現実的なリアルタイム補聴器処理のコンテキストやフィールド条件下でモバイル処理プラットフォームに組み込んで新しいアルゴリズムをテストしたいという要望がしばしば生じます。

openMHA は限られたハードウェアでもリアルタイムオーディオ処理が可能な強力で柔軟なツールセットを提供しますが、C++ で書かれています。高度な信号処理アルゴリズムを MATLAB コードから C++ に移植するのは手間がかかり、人員不足や C++ の専門知識の不足により、時に乗り越えられない障壁となることがあります。

このドキュメントでは、MATLAB Coder による C/C++ への変換を通じて、ユーザーの MATLAB コードをプラグインとして openMHA に統合する方法を説明します。

### 用語

- **ユーザーコード**: MATLAB Coder 経由で openMHA に統合したい MATLAB コード
- **ユーザー関数**: ユーザーコード内のエントリーポイント関数とその変換形式
- **生成コード**: Coder がユーザーコードから生成する C/C++ ソースコード
- **ユーザーライブラリ**: 生成コードからコンパイルされた共有ライブラリ
- `this` のようなテキストはソースコード内の変数名や構造体名、`call()` は関数を指します。`this.m` はファイル名を意味します

### 前提条件

- openMHA のコピー（ソースコードまたはバイナリ形式）
- MATLAB Coder ライセンス
- openMHA の基本的な使用方法の理解
- コンパイラ、ソースコード、プラグイン、MATLAB 構造体についての基本知識

詳細は openMHA アプリケーションマニュアルを参照してください。

### ドキュメント構成

生成コードを openMHA プラグインとして統合する方法は2つあります:

1. **matlab_wrapper プラグイン**: 使いやすいが柔軟性が低い。ユーザーライブラリ名をプラグインに提供し、プラグインがユーザー関数を適切なタイミングで呼び出します
2. **ネイティブコンパイル**: より柔軟だが、ユーザーが開発環境のセットアップとある程度の C++ 知識を必要とします

### どちらのアプローチを使用するか

**matlab_wrapper プラグインが推奨される場合:**
- C++ の専門知識がほとんどない
- ユーザーコードに状態が少ない（ブロック間で保持するデータが少ない）
- 実行時の設定がほとんど不要
- モノリシックな構造（1つの大きなブラックボックス）
- openMHA の他の部分との相互作用が少ない

**ネイティブコンパイルが推奨される場合:**
- オーディオ信号以外の openMHA とのデータ共有が必要
- アルゴリズム構造自体が変更対象
- モジュール性を保持する必要がある
- ラッパープラグインの規定構造へのリライトが不可能

## MATLAB Coder の概要

MATLAB Coder は MATLAB コードから C/C++ コードを生成します。生成されたコードは MATLAB コンパイラまたは他のコンパイラでコンパイルできます。生成コードは、ソースコード形式または matlab_wrapper プラグイン経由のコンパイル形式で openMHA に統合できます。matlab_wrapper プラグインはコンパイル済みの C コードのみ受け入れます。

### エントリーポイント関数

エントリーポイント関数は C/C++ コードにコンパイルされるトップレベル MATLAB 関数です。エントリーポイントとしてマークされた関数のみが、外部から呼び出し可能な関数として生成されることが保証されます。

### 入力型

C は静的型付けのため、すべての入出力型はコンパイル時に既知である必要があります。MATLAB とは異なり、配列のサイズを含む入出力型は関数シグネチャの一部となり、後から変更できません。

MATLAB Coder は double、single、half 精度浮動小数点数、8/16/32/64 ビット符号付き/符号なし整数、論理値、文字、構造体、セル配列、文字列を扱えます。

## matlab_wrapper プラグインの使用方法

matlab_wrapper プラグインは、MATLAB コードを openMHA に統合する最も簡単（だが最も制約の多い）方法です。ユーザーコードを共有ライブラリにコンパイルし、`library_name` 設定変数にライブラリ名（拡張子なし）を指定します。

### ユーザーコードの構造

ユーザーコードとプラグインは4つのエントリーポイント関数でインターフェースします:
- `init()` — ライブラリ読み込み時に呼び出し
- `prepare()` — prepare コマンド発行時に呼び出し
- `process_xy()` — 信号処理（xy は ww/ss/ws/sw のいずれか）
- `release()` — クリーンアップ

このうち `process()` は必須です。

#### init()

```matlab
function [user_config,state] = init(user_config,state)
```

`user_config` は以下のメンバーを持つ構造体の `1xInf` 配列です:
- **name**: `1xInf` 文字配列（設定変数名）
- **value**: `InfxInf` double 配列

ユーザー定義の設定変数が必要な場合、`init()` 内で作成します:

```matlab
function [user_config,state] = init(user_config,state)
  user_config = [struct('name','writeable', 'value',ones(1,1))];
end
```

`state` 変数も同様に初期化され、`process()` 呼び出し間のデータ保持に使用されます:

```matlab
function [user_config,state] = init(user_config,state)
  state = [struct('name','rmslevel','value',ones(1,1))];
end
```

#### prepare()

信号の形状に依存するすべての初期化はここで行います。入力信号のプロパティの確認も可能です。処理が信号のプロパティを変更する場合、`signal_dimensions` の適切なメンバーを変更する必要があります。

```matlab
function [signal_dimensions, user_config, state] = ...
         prepare(signal_dimensions, user_config, state)
  user_config(1).value(1,1) = 2;
  state(1).value = zeros(signal_dimensions.channels);
  signal_dimensions.channels = uint32(1);
end
```

`signal_dimensions` のメンバー:
- **channels**: チャンネル数（uint32）
- **domain**: 'W'（波形）または 'S'（スペクトル）
- **fragsize**: フラグメントサイズ（uint32）
- **wndlen**: FFT のウィンドウ長（スペクトル領域の場合、それ以外は0）
- **fftlen**: FFT 長（スペクトル領域の場合、それ以外は0）
- **srate**: サンプリング周波数（double）

#### process_xy()

すべての信号処理は `process_xy()` 関数で行います。'xy' は入出力信号ドメインによって異なります:
- `ww`: 波形→波形
- `ss`: スペクトル→スペクトル
- `ws`: 波形→スペクトル
- `sw`: スペクトル→波形

```matlab
function [s_out,user_config,state] = process_xy(s_in,...
                                          signal_dimensions,...
                                          user_config,state)
```

#### release()

```matlab
function release()
  ...
end
```

### ユーザー設定

`user_config` の各要素に対して、同名の openMHA 設定変数が作成され、リアルタイムセーフな方法で変更できます。

現在の制限: `process()` 中の `user_config` への変更はパーサー側からの設定変更時に失われるため、フィルタ状態などの動的状態には `state` を使用してください。

### 状態保持

状態保持には2つの方法があります:

1. **persistent/global 変数**: 簡単だが、ユーザーライブラリの複数インスタンス間で共有されるため注意が必要
2. **state 入出力変数**: `user_config` と同じ型。すべての要素は `init()` で初期化が必要。`process()` 中はサイズ変更不可（クラッシュの原因になります）

### デプロイメント

MATLAB Coder にコンパイラを設定する必要があります。互換性の問題を避けるため、以下のコンパイラの使用を推奨します:
- **Windows**: MinGW コンパイラ
- **Linux**: gcc コンパイラ
- **macOS**: clang

ユーザーライブラリ（共有ライブラリ: `.so`/`.dylib`/`.dll`）を openMHA がプラグインを探すディレクトリにコピーします:
- **Windows**: `C:\Program Files\openMHA\bin`
- **macOS**: `/usr/local/lib/openmha`
- **Linux**: `/usr/lib`

### サンプル

`examples/24-matlab-wrapper-simple` から `examples/25-matlab-wrapper-advanced` のコードに至る手順:

#### init.m

```matlab
function [user_config, state] = init(user_config, state)
  user_config = [struct('name','delay', 'value',ones(1,1)); ...
                 struct('name','gain','value',ones(1,1))];
end
```

#### prepare.m

```matlab
function [signal_dimensions, user_config, state] = ...
         prepare(signal_dimensions, user_config, state)
  if(signal_dimensions.domain~='W')
    fprintf('This plugin can only process signals in the time domain.\n');
    assert(false);
  end
  user_config(1).value = zeros(signal_dimensions.channels,1);
  user_config(2).value = zeros(signal_dimensions.channels,1);
  signal_dimensions.channels = uint32(1);
end
```

#### process.m（遅延加算アルゴリズム）

```matlab
function [wave_out,user_config,dummy] = ...
         process(wave_in,signal_dimensions, user_config, dummy)
  delay = user_config(1).value;
  gain = user_config(2).value;

  persistent state;
  if(isempty(state))
    state = zeros(signal_dimensions.fragsize+uint32(max(delay(:))),...
                  signal_dimensions.channels);
  end

  persistent read_idx;
  if(isempty(read_idx))
    read_idx = uint32(zeros(signal_dimensions.channels));
  end

  persistent write_idx;
  if(isempty(write_idx))
    write_idx = delay;
  end

  for fr=1:signal_dimensions.fragsize
    for ch=1:signal_dimensions.channels
      write_idx(ch) = mod(write_idx(ch),...
                          (signal_dimensions.fragsize+delay(ch)))+1;
      state(write_idx(ch),ch) = wave_in(fr,ch);
    end
  end

  wave_out = zeros(signal_dimensions.fragsize,1);
  for fr=1:signal_dimensions.fragsize
    for ch=1:signal_dimensions.channels
      read_idx(ch) = mod(read_idx(ch),...
                         (signal_dimensions.fragsize+delay(ch)))+1;
      wave_out(fr) = wave_out(fr) + state(read_idx(ch),ch)*10^(gain(ch)/10);
    end
  end
end
```

#### コード生成

```matlab
make('ww','outputName','example_25','packOutput',true);
```

#### openMHA 設定ファイルの例

```
nchannels_in = 2
fragsize = 128
srate = 16000

iolib = MHAIOFile
io.in = example_25.wav
io.out = out.wav

mhalib = matlab_wrapper
mha.library_name = example_25
cmd = prepare
mha.delay = [50 100]
mha.gain = [-5 -5]
```

## ネイティブコンパイル

ラッパープラグインの制約に合わせてコードをリライトできない場合や、アルゴリズムの一部のみを MATLAB で実装したい場合は、「ネイティブコンパイル」アプローチを使用できます。

ユーザーはスケルトン openMHA プラグインのソースコードを基に独自のプラグインを作成し、生成コードをビルディングブロックとして使用し、他の自作 openMHA プラグインと同様にコンパイルします。

このアプローチはより柔軟ですが、ユーザー側でより多くの対応が必要です。設定パラメータの受け渡しには、MATLAB 関数の入力引数として定義し、`MHAParser::*` 設定変数を手動で追加して適切な型に変換する必要があります。

初心者向けのサンプルは `examples/23-matlab-coder` を参照してください。
