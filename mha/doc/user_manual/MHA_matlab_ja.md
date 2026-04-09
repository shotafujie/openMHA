# Octave/Matlab ツール

> この文書は [MHA_matlab.tex](MHA_matlab.tex) の日本語訳です。

## 概要

このパッケージリリースには、Octave および Matlab で使用するための openMHA 関連ツールが含まれています。これらのモジュールに対するサポートや保証は提供されません。

openMHA フレームワークはシンプルな Octave/Matlab インターフェース（mhactl）を通じて制御できます。このツールは openMHA フレームワークへの TCP 接続を開き、フレームワーク設定インターフェースと通信します。

openMHA とのデータ交換のために、JACK 低遅延サウンドサーバー（[MHA_system_ja.md](MHA_system_ja.md) 参照）への Octave/Matlab クライアントがこのリリースに含まれています。このインターフェースにより、特別なツールボックスを必要とせずに、Octave および Matlab から低遅延リアルタイム処理システムに直接アクセスできます。

アルゴリズム通信変数は `acsave` アルゴリズムを使用して Matlab 形式のファイルにエクスポートできます。

## mhactl_wrapper - Octave/Matlab 用 openMHA 制御インターフェース

Octave/Matlab 関数 `mhactl_wrapper` は、TCP ネットワーク接続を通じて openMHA フレームワークと通信します。

正しく動作するためには、openMHA フレームワークがデフォルトの確認応答/プロンプト文字列で起動されている必要があります。MHA プロセスが Octave または Matlab と同じユーザーや同じマシンで実行されている必要はありません。

関数 `mhactl_wrapper` は2つの引数を受け取ります: openMHA ハンドル（正しい TCP ポートとホストを持つ構造体）と、処理する openMHA クエリです:

```matlab
result = mhactl_wrapper( mha_handle, query )
```

`mhactl_wrapper` 関数は openMHA フレームワークへのネットワーク接続を開き、コマンド文字列を MHA に送信し、確認応答プロンプトを待ちます。成功した場合、MHA の応答（確認応答プロンプトなし）が返されます。そうでなければエラーが報告されます。

## mhactl_wrapper のラッパー関数

`mhactl_wrapper` は openMHA 制御インターフェースへの直接アクセスを提供しますが、`mhactl_wrapper` を利用して openMHA 制御コマンドを Octave/Matlab の値に変換したり、その逆を行ったりするラッパー関数がいくつか実装されています。

### mha_get - openMHA 設定の内容を読み取る

関数 `mha_get` は openMHA 設定エントリの内容を読み取り、Octave/Matlab の型で返します（openMHA の文字列表現からの型依存の変換が行われます）。コマンド構文は:

```matlab
[answer, info] = mha_get(handle, field, perm)
```

openMHA ハンドル `handle` は、openMHA フレームワークのホスト名とポート番号を定義するフィールド `host` と `port` を含む構造体です。

`field` は openMHA 設定エントリの名前です。変数またはパーサーノードのいずれかです。変数の場合、変数の内容が `answer` に、変数のヘルプコメントが `info` に返されます（利用可能な場合）。

`field` がパーサーノードを示す場合、`answer` は Octave/Matlab の構造体を保持し、各フィールドが openMHA 変数またはサブパーサーの内容を持ちます。この場合、特定のパーミッションを持つエントリのみにクエリを制限できます。パーミッションは `perm` で指定でき、文字列またはセル配列のいずれかです。

openMHA フレームワークの完全な書き込み可能設定を取得するには:

```matlab
cfg = mha_get( handle, '', 'writable' )
```

### mha_set - openMHA 設定エントリの内容を設定する

Octave/Matlab の値を `mha_set` 関数で openMHA 設定エントリに割り当てることができます。

構文:

```matlab
mha_set( handle, field, value )
```

`mha_get` と同様に、`handle` は openMHA フレームワークのホスト名とポート番号を定義するフィールド `host` と `port` を含む構造体で、`field` は openMHA 設定エントリの名前です。

パラメータ `value` は変数 `field` に割り当てられる Matlab 表現です。Octave/Matlab 表現は、制御インターフェースを通じて設定エントリ `field` の型を最初に取得することで、正しい openMHA 文字列表現に変換されます。Octave/Matlab の値が変換できない場合、エラーが報告されます。

完全な openMHA を設定するために、Octave/Matlab の設定構造体 `cfg` を以下のように openMHA に割り当てることができます:

```matlab
mha_set( handle, '', cfg )
```

## mhagui_generic - 汎用グラフィカルユーザーインターフェース

openMHA フレームワークへの汎用グラフィカルユーザーインターフェース（GUI）が、関数 `mhagui_generic` とヘルパー関数 `mhagui_*.m` を通じて利用可能です。

GUI 関数の構文:

```matlab
h = mhagui_generic( handle, base )
```

`handle` は openMHA フレームワークのホスト名とポート番号を定義するフィールド `host` と `port` を含む構造体です。デフォルト値は `localhost` と 33337 です。

`base` は openMHA パーサーノードの名前です（デフォルト: `''`、つまりルートレベル）。

Octave/Matlab フィギュアにコントロールパネルが作成され、フィギュアハンドルが返されます。パーサー `base` の各エントリにコントロール要素が作成されます:

- 数値スカラーはスライダーとして表示
- キーワードリストは選択ボックスとして表示
- ブール値エントリはトグルボタンとして表示
- 浮動小数点値のベクトルにはスライダー配列のウィンドウを開くことが可能
- サブパーサーは独自のコントロールパネルを含む新しいウィンドウとして開くことが可能
- その他の型はテキスト編集フィールドで編集可能

openMHA が Octave/Matlab 制御インターフェースと同じホストで実行されている場合、`read` または `save` ボタンをクリックして openMHA 設定ファイルを読み取りおよび保存できます。read/save コマンドはコントロールパネルに表示されている openMHA パーサーレベルからの相対操作です。つまり、完全な設定はルートレベルパネルから読み取りまたは保存する必要があります。

![openMHA フレームワークの汎用 GUI](../images/mhagui_generic.pdf)
*図: Octave/Matlab の関数 `mhagui_generic` で作成された openMHA フレームワークの汎用グラフィカルユーザーインターフェース*
