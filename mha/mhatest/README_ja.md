# MatlabUnit：MATLAB用単体テストフレームワーク

[原文](README.txt)の日本語訳です．原文はドイツ語です．Copyright © 2003–2005 Medizinische Physik，Universität Oldenburg．著者：Tobias Herzke．ファイル版：2005-04-13，1.2．

これはMedi-Akuコロキウムで紹介したMATLAB用単体テストフレームワークです．発表スライドは `test_driven_development.pdf` にあります．以下ではテスト対象のコードをProgram Logic，検証するコードをTest Casesと呼びます．

各テストケースは，`test_*.m` という名前のmファイル内のMATLAB関数として実装します．テスト対象の関数を呼び出し，結果が期待と一致するかを `assert_*.m` 関数で検査します．等値，不等値，差の小ささ，MATLABの真偽値を検査できます．アサーションを満たさない場合や実行中にエラーが起きた場合は失敗，最後までエラーなく実行できれば成功です．

ディレクトリ内の全テストを順番に実行するには `runtests.m` を呼び出します．カレントディレクトリ，または引数で指定したディレクトリから，`test_*.m` という名前のテストを見つけて実行します．成功・失敗を集計し，最後に概要を表示します．

```text
33 tests: 133 assertions, 0 failures, 0 errors, 0 teardown errors
```

この例では33個のテストファイルで計133回のアサーションを実行しています．アサーション失敗，MATLABエラー，後片付け時のエラーはいずれも0です．

## teardown errorsとは

テストが生成したファイルや，初期化したsoundmexなどの共有資源は，テスト後に解放する必要があります．

```matlab
soundmex init;
testing_mem2mem;
soundmex exit;
```

この例では `testing_mem2mem` 中にエラーが起きると `soundmex exit` が実行されません．そこで，成功・中断にかかわらずテスト終了後に必ず実行する後片付け関数を登録できます．登録関数は `unittest_teardown` で，後で内部的に `feval` を呼ぶため，引数の渡し方も `feval` と同じです．複数の後片付け関数を登録でき，登録と逆順（後入れ先出し）で実行されます．

訳注：これはMATLAB側の旧来のフレームワークの説明です．C++の単体テストはルートの `make unit-tests` で実行します．
