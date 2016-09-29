# fastText Japanese Tutorial

Facebookの発表した[fastText](https://github.com/facebookresearch/fastText)を日本語で学習させるためのチュートリアルです。

## Setup

事前に、以下の環境のセットアップを行います。Windowsの場合、MeCabのインストールが鬼門のためWindows10ならbash on Windowsを利用してUbuntu環境で作業することを推奨します。

* Install Python (above 3.5.2)
* Install [MeCab](http://taku910.github.io/mecab/)
* Download (`git clone`) [WikiExtractor](https://github.com/attardi/wikiextractor)
* Download (`git clone`) [fastText](https://github.com/facebookresearch/fastText)

## 1. 学習に使用する文書を用意する

日本語Wikipediaのダンプデータをダウンロードし、 `source` フォルダに格納してください。  


## 2. テキストを抽出する

WikiExtractorを使用し、sourceに格納したWikipediaのデータからテキストを抜き出し、`corpus`フォルダに格納します。

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
python parse.py (対象フォルダ) --concat (対象ファイルに共通する名称(wiki_など))
```

これで、学習用のテキストデータの作成が完了しました。

## 3. テキストを単語に分ける(分かち書きする)

テキストデータ内の単語を英語と同じようにスペースで分ける作業(=分かち書き)を行います。この作業には、MeCabを利用します。

```
mecab (対象テキストファイル) -O wakati -o (出力先ファイル)
```

これで、単語ごとに区切られたファイルができました。

## 4. fastTextで学習する

英語と同じように、単語ごとに区切られたファイルが手に入ったため、あとはfastTextを実行するだけです。[fastText](https://github.com/facebookresearch/fastText)のリポジトリをcloneしてきて、ドキュメントにある通りmakeによりビルドしてください。

設定パラメーターは各種ありますが、論文を参考にすると、扱うデータセットにより単語の数値表現のサイズ(ベクトルの次元)は以下のようになっています(※tokenが何の単位なのかは言及がなかったのですが、おそらく単語カウントと思われます)。

* small(50M tokens): 100
* mediam(200M tokens) :200
* full:300

要は、小さいデータセットなら小さい次元、ということです。Wikipedia全件のような場合はfullの300次元に相当するため、以下のように処理します。

```
./fasttext skipgram -input (分かち書きしたファイル) -output model -dim 300
```

Word2Vecの学習と同等のパラメーターで行う場合は、以下のようになります(パラメーター設定などは、[こちら](http://aial.shiroyagi.co.jp/2015/12/word2vec/)に詳しいです)。

```
./fasttext skipgram -input (分かち書きしたファイル) -output model -dim 200 -neg 25 -ws 8
```

(Issueにも上がっていますが、[パラメーターで結構変わる](https://github.com/facebookresearch/fastText/issues/5)らしいです。epoch、mincountなど。。。)

学習が完了すると、`-output`で指定したファイル名について、`.bin`と`.vec`の二種類のファイルが作成されます。これらが学習された分散表現を収めたファイルになります。
ただ、Wikipeida全件のような場合はデータサイズが大きすぎて`model`のファイルを読み込もうとするとMemoryErrorで飛ぶこともままあるほか、エンコードの問題が発生するケースがあります(というか発生したのですが)。そのような場合は、一旦単語の辞書を作り(「朝」->11など、単語をIDに変換する辞書を作る)、テキストファイルを単語IDの列に変換するなどして対応します。
この作業のために、`parser.py`にtokenizeの機能を実装しているので、必要に応じて活用してください。

```
python parser.py (対象テキストファイル)  --tokenize
```

これで、`.vocab`という辞書ファイルと、`_tokenized`という単語ID化されたテキストファイルが手に入ります。


## 5.fastTextを活用する

`eval.py`を利用し、似ている単語を検索することができます。

```
python eval.py (単語)
```

こちらは、デフォルトで`fastText`内の`model.vec`を参照します。別のファイル名、または別の場所に保管している場合は`--path`オプションで位置を指定してください。

