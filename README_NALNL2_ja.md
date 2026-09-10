# NAL-NL2フィッティングルール

[英語原文](README_NALNL2.md)／対応：openMHA 4.18.1（上流 `0b9f087e`）．

openMHAはオープンソース製品で，非商用の補聴器用ダイナミックコンプレッサ処方ルールを含みます．National Acoustic Laboratories（NAL）の商用処方ルールNAL NL2でフィッティングすることも可能です．WindowsとLinuxで利用でき，NAL-NL2ラッパーとNAL-NL2 DLLの導入が必要です．

## ラッパーのインストール

クローズドソース版MHAまたはopenMHAのコンプレッサをNAL NL2でフィッティングするには，NAL-NL2.DLLと，DLLをMATLAB／OctaveベースのGUIに接続するコマンドラインラッパーが必要です．

原文が示すラッパーのパスは `mha/tools/fitting/NAL-NL2/nalnl2wrapper.exe` です．訳注：このチェックアウトに実行ファイルは含まれていません．[ビルド手順](mha/tools/fitting/NAL-NL2/README_ja.md)も参照してください．このラッパーはopenMHAプロジェクトの一部ではありません．動作に必要なNAL NL2 DLLはNALから購入する必要があります．

### Linux

1. `/usr/share/nalnl2wrapper` ディレクトリを作成します．
2. `nalnl2wrapper.exe` をそのディレクトリへ配置します．
3. 正規にライセンスされた `NAL-NL2.dll` を同じディレクトリへ配置します．
4. 次を実行します．

```sh
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install wine32:i386
```

### Windows

1. `C:\Program Files\nalnl2wrapper` ディレクトリを作成します．
2. `nalnl2wrapper.exe` をそこへ配置します．
3. 正規にライセンスされた `NAL-NL2.dll` を `C:\Program Files\nalnl2wrapper\bin` へ配置します．

訳注：WindowsのDLL配置先は原文どおりです．この手順の実機検証は行っていません．

これにより，フィッティングGUI `mhagui_fitting` と `mhagui_fitting_offline` で，コンプレッサの処方ルールとしてNAL NL2を選択できます．

研究に使用する前に，適用するNAL NL2フィッティングを確認してください．openMHAコンプレッサ向けの挿入利得の計算は `gainrule_NAL_NL2.m` に記載されています．期待する計算と一致するか確認し，誤りや不正確な点があれば [openMHAのIssues](https://github.com/HoerTech-gGmbH/openMHA/issues) へ報告してください．
