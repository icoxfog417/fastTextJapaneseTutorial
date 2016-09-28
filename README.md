# fastText Japanese Tutorial

Facebookの発表した[fastText](https://github.com/facebookresearch/fastText)を日本語で学習させるためのチュートリアルです。

## Setup

事前に、以下の環境のセットアップを行います。Windowsの場合、MeCabのインストールが鬼門のためWindows10ならbash on Windowsを利用してUbuntu環境で作業することを推奨します。

* Install Python (above 3.5.2)
* Install [MeCab](http://taku910.github.io/mecab/)
* Download (`git clone`) [WikiExtractor](https://github.com/attardi/wikiextractor)

## 1. Download Wikipedia Dump

日本語Wikipediaのダンプデータをダウンロードし、 `source` フォルダに格納してください。  
その後、以下のコマンドを実行し、WikiExtractorにより`corpus`フォルダにテキストを抽出したデータを格納します。

```
python wikiextractor/WikiExtractor.py -b 500M -o corpus source/jawiki-xxxxxxxx-pages-articles-multistream.xml.bz2
```

* `-b`は、抽出したデータそれぞれのファイルサイズで、この単位でテキストファイルが作成されていきます。必要に応じ調整をしてください。

Wikipediaのabstractのファイルを使う場合は、`parse.py`にabstract用の抽出処理を実装しているので、そちらを利用してください。

```
python parse.py jawiki-xxxxxxxxx-abstract4.xml  --extract
```

テキストを抽出したファイルは、最終的に一つにまとめます。これはコマンドで行ってもよいですが、`parse.py`に結合用のスクリプトを用意しているのでコマンドがわからない場合は使ってください。

```
python parse.py target_folder --concat file_prefix
```

これで、学習用のテキストデータの作成が完了しました。

## 2. Tokenize text file

テキストデータ内の単語を英語と同じようにスペースで分ける作業(=分かち書き)を行います。この作業には、MeCabを利用します。

```
mecab (対象テキストファイル) -O wakati -o (出力先ファイル)
```

これで、単語ごとに区切られたファイルができました。

## 3. Train fastText

英語と同じように、単語ごとに区切られたファイルが手に入ったため、あとはfastTextを実行するだけです。[fastText](https://github.com/facebookresearch/fastText)のリポジトリをcloneしてきて、ドキュメントにある通りmakeによりビルドしてください。

設定パラメーターは各種ありますが、論文を参考にすると、扱うデータセットにより単語の数値表現のサイズ(ベクトルの次元)は以下のようになっています。

* small: 100
* mediam:200
* full:300

Wikipedia全件のような場合はfullの300次元に相当するため、以下のように処理します。

```
./fasttext skipgram -input (分かち書きしたファイル) -output model -dim 300
```

Word2Vecの学習と同等のパラメーターで行う場合は、以下のようになります(パラメーター設定などは、[こちら](http://aial.shiroyagi.co.jp/2015/12/word2vec/)に詳しいです)。

```
./fasttext skipgram -input (分かち書きしたファイル) -output model -dim 200 -neg 25 -ws 8
```

(Issueにも上がっていますが、[パラメーターで結構変わる](https://github.com/facebookresearch/fastText/issues/5)らしいです。epoch、mincountなど。。。)





