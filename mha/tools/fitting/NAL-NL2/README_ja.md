# NAL NL2ラッパーのビルド

[原文](README.txt)の日本語訳です．

このディレクトリにはNAL NL2 DLL用コマンドラインラッパーのソースコードがあります．通常の導入方法は [README_NALNL2_ja.md](../../../../README_NALNL2_ja.md) を参照してください．この文書は，変更したラッパーを再ビルドするための説明です．

必要なものはWindows，[MSYS2](https://www.msys2.org/)，MSYS2の `make` と `mingw32/mingw-w64-i686-gcc` パッケージ，NALが提供する `NAL-NL2.lib` と `NAL-NL2.dll` です．

NAL NL2 Developer Kitの両ファイルをこのディレクトリへ配置します．MSYS2のMinGW 32ビットターミナルを開き，このディレクトリへ移動して `make` を実行してください．
