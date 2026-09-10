# DSLmio 5によるフィッティング

[原文](README_DSLmio5.md)の日本語訳です．対応：上流 `0b9f087e`．原文にはUbuntu 20.04を前提とする旧来の手順が残っています．ここでは原文を訳し，現在の配布状況や実機動作は確認していません．C++本体のビルドにこの商用ルールは必要ありません．

openMHAはオープンソース製品で，非商用の補聴器用ダイナミックコンプレッサ処方ルールを含みます．University of Western Ontario（UWO）の商用処方ルールDSLmio 5も利用できます．

原文ではLinuxで利用でき，Windowsへの対応を進めていると説明しています．Windowsでフィッティングしたい場合は，[developmentブランチの最新版](https://github.com/HoerTech-gGmbH/openMHA/blob/development/README_DSLmio5.md)にWindows用の手順があるか確認してください．

DSLmio 5を使用するには，次の手順を実施します．

1. Ubuntu 20.04を導入した64ビットPCを用意します．
2. UWOから64ビットLinux用DSLmio 5のDLL版を購入します．`libDSLmio-core.so`，`libDSLmio-core.so.5`，`libDSLmio-core.so.<Version>+build.<BuildNo>`，`dslmio.dat` の全ファイルとシンボリックリンクを `/usr/lib` へコピーします．
3. [インストール手順](INSTALLATION_ja.md)に従ってopenMHAを導入します．
4. `apt install dsl-wrapper` でラッパーを導入します．Octaveが未導入なら，これもインストールされます．
5. Octaveを起動します．`mhacontrol` または `mhagui_fitting` で別途起動したopenMHAをフィッティングできます．`mhagui_fitting_offline` ではOctave内から音声ファイルへ補聴器のダイナミック圧縮を適用できます．これらのツールにDSLの選択肢が追加されます．

研究に使用する前に適用するフィッティングを確認してください．挿入利得の計算は `gainrule_DSLmio5.m` にあります．期待と一致するか確認し，誤りや不正確な点は [openMHAのIssues](https://github.com/HoerTech-gGmbH/openMHA/issues)へ報告してください．
