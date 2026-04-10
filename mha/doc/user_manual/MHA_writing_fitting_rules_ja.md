# フィッティングルールの記述

> [English version (LaTeX)](MHA_writing_fitting_rules.tex)

**注意**: フィッティングインターフェースは完全な再設計が予定されています。

## ゲイン処方ルール

40% ゲインルールを例にしたゲイン処方ルールの記述方法:

```matlab
function sGt = gainrule_linear40( sAud, sCfg )
  nLev = length(sCfg.levels);
  htl.l = interp1(log(sAud.frequencies),sAud.l.htl,...
          log(sCfg.frequencies),'linear','extrap');
  htl.r = interp1(log(sAud.frequencies),sAud.r.htl,...
          log(sCfg.frequencies),'linear','extrap');
  sGt = struct;
  sGt.l = repmat(0.4*htl.l,[nLev 1]);
  sGt.r = repmat(0.4*htl.r,[nLev 1]);
```

### 入力引数

**`sAud`** — サブ構造体 `l` と `r` を持つ構造体です。それぞれ純音オージオグラム（HTL、測定されている場合は UCL）を含みます。周波数は `sAud.frequencies` に格納されます。測定されていない値は `inf` または `nan` として格納されます。

**`sCfg`** — コンプレッサモジュールの設定情報を含む構造体です:
- `sCfg.levels`: ゲインサンプルが期待される入力レベル値
- `sCfg.frequencies`: コンプレッサフィルタバンクの中心周波数
- `sCfg.edge_frequencies`: コンプレッサフィルタバンクのエッジ周波数（フィルタの -3 dB ポイント）

### 出力

**`sGt`** — 左右のゲインを含む構造体です。`sGt.l` と `sGt.r` のそれぞれが N_level × M_freq のサイズの行列で、N_level はレベルサンプル数、M_freq は周波数帯域数です。
