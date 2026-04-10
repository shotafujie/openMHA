# 15-ac-variables: AC 変数の使い方

> [English version](README.txt)

このディレクトリには AC 変数の使用方法に関するサンプルが含まれています。

openMHA 設定ファイル `acvars_simple_example.cfg` は、2つの `rmslevel` プラグインと1つの `gain` プラグインを含む信号処理チェーンを読み込みます。2つの `rmslevel` プラグインは、ゲインプラグインの前後の信号レベルを測定します。

ゲインプラグインは右チャンネルを増幅し、左チャンネルはそのまま通過させるように設定されています。

両方の `rmslevel` プラグインは、設定名 `L1` および `L2` で読み込まれ、測定された音圧レベルを含む AC 変数を生成します（openMHA_application_manual.pdf のセクション 2.2 参照）。プラグインが作成する AC 変数を確認するには、`analysemhaplugin` をプラグイン名をパラメータとして実行します:

```
analysemhaplugin rmslevel
```

出力の最初の約20行を読むと、以下のような AC 変数が確認できます:

```
-- waveform processing ---------------------------
empty AC space before prepare.
Successfully prepared for waveform processing.
AC variables after prepare:
  rmslevel_level
  rmslevel_level_db
  rmslevel_peak
  rmslevel_peak_db
```

dB でのレベルは、デフォルトでは `rmslevel_level_db` という名前の変数に格納されます。この設定では `rmslevel` プラグインを設定名 `L1` および `L2` で読み込んでいるため、AC 変数名は `L1_level_db` と `L2_level_db` になります。これは設定名を指定して確認できます:

```
analysemhaplugin rmslevel:L1
```

設定ファイルの処理後、ゲイン適用前後の両チャンネルのレベルが表示されます:

```
mha "?read:acvars_simple_example.cfg"

[6.5034132 5.51731634]
[6.5034132 11.5173197]
```

左チャンネルのレベルはゲインプラグインで変更されていませんが、右チャンネルのレベルは予想通り6 dB増加しています。詳細は設定ファイルを参照してください。
