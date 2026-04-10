# 33-compile-plugin-on-PHL: PHL でのプラグインコンパイル

> [English version](README.md)

openMHA のプラグイン開発ガイド（http://www.openmha.org/documentation/ からリンク）には、C++ で openMHA プラグインを書くチュートリアルが含まれています。C++ コードは openMHA で使用する前にコンパイルする必要があります。

このディレクトリには、サンプルプラグインのソースコード `example33.cpp` と、Mahalia 4.18.0-r0 以降を実行する Portable Hearing Laboratory（PHL）上でプラグインをコンパイルするための `Makefile` が含まれています。

## プラグインソースコードの PHL への転送

コードは PHL 上でコンパイルする必要があるため、まずデバイスに転送します。WiFi 経由で PHL に接続し、コードをコピーします（パスワード: mahalia）:

```
scp example33.cpp Makefile mha@10.0.0.1:
```

初回接続時に「接続を続行するか」を確認された場合は「yes」と回答してください。

以前別の PHL デバイスに接続していた場合、セキュリティ上の理由で接続が拒否されることがあります。以下で解決できます:

```
ssh-keygen -R 10.0.0.1
```

## PHL でのコンパイル

SSH で PHL に接続します（パスワード: mahalia）:

```
ssh mha@10.0.0.1
```

ソースコードと Makefile が含まれるディレクトリ（ログイン後のカレントディレクトリ、すなわち mha ホームディレクトリ）で以下を実行:

```
make
```

コンパイルには約1分かかります。プラグインを openMHA で利用可能にするには、生成された `*.so` ファイルを `/usr/lib` にコピーします:

```
sudo cp example33.so /usr/lib
```

## プラグインの使用

自作プラグインは他のプラグインと同様に openMHA 設定で使用できます。ここでコンパイルしたプラグインは、拡張子なしのファイル名「example33」として参照されます。
