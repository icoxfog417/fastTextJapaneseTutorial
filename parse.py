import os
import argparse
import xml.etree.ElementTree as ET


MAKE_CORPUS_PATH = lambda f: os.path.join(os.path.dirname(__file__), "./corpus/" + f)


def extract(file_path):
    if not os.path.isfile(file_path):
        raise Exception("Abstract file does not found.")
    root = ET.parse(file_path)
    root.findall(".")

    file_path = MAKE_CORPUS_PATH("abstracts.txt")
    stream = open(file_path, mode="w", encoding="utf-8")

    for doc in root.findall("./doc"):
        abs = doc.find("./abstract").text
        if not abs:
            continue
        elif abs.startswith(("|", "thumb", "{", "・", ")", "(", "link")):
            continue
        title = doc.find("./title").text.replace("Wikipedia: ", "")

        if abs and title:
            stream.write(title + "\n")
            stream.write(abs + "\n")
    
    stream.close()


def concat(dir, prefix):
    if not os.path.isdir(dir):
        raise Exception("directory is not found")
    
    paths = []
    def fetch(_dir):
        files = os.listdir(_dir)
        for f in files:
            p = os.path.join(_dir, f)
            if os.path.isfile(p) and f.startswith(prefix):
                paths.append(p)
            if os.path.isdir(p):
                fetch(p)
    
    fetch(dir)
    file_path = MAKE_CORPUS_PATH(prefix + "_all.txt")
    with open(file_path, mode="w", encoding="utf-8") as o:
        for p in paths:
            print("concat {}.".format(p))
            with open(p, mode="r", encoding="utf-8") as f:
                for line in f:
                    o.write(line)


def wakati(file_path):
    from janome.tokenizer import Tokenizer
    path, ext = os.path.splitext(file_path)
    wakati_path = path + "_wakati" + ext

    tokenizer = Tokenizer()

    def wsplit(text):
        ws = []
        tokens = tokenizer.tokenize(text.strip())
        for t in tokens:
            w = t.surface.strip()
            if w:
                ws.append(w)
        return ws

    with open(file_path, mode="r", encoding="utf-8") as f:
        with open(wakati_path, mode="w", encoding="utf-8") as w:
            for line in f:
                words = wsplit(line)
                w.write(" ".join(words) + "\n")


def tokenize(file_path, vocab_size):
    import MeCab
    path, ext = os.path.splitext(file_path)
    vocab_path = path + ".vocab"
    tokenized_path = path + "_tokenized" + ext
    UNKNOWN = 0

    tagger = MeCab.Tagger("-Owakati")
    tagger.parse("")

    def wsplit(text):
        ws = []
        node = tagger.parseToNode(text.strip())
        while node:
            w = node.surface.strip()
            if w:
                ws.append(w)
            node = node.next
        
        return ws

    # make vocab file
    print("making vocabulary dictionary...")
    vocab = {}
    with open(file_path, mode="r", encoding="utf-8") as f:
        for line in f:
            words = wsplit(line)
            for w in words:
                if w in vocab:
                    vocab[w] += 1
                else:
                    vocab[w] = 1

    dictionary = [UNKNOWN] + sorted(vocab, key=vocab.get, reverse=True)
    dictionary = dictionary[:vocab_size]
    with open(vocab_path, mode="w", encoding="utf-8") as v:
        v.write("\n".join([str(_v) for _v in dictionary]))

    # make tokenized file
    print("tokenize by vocabulary dictionary...")        
    with open(file_path, mode="r", encoding="utf-8") as f:
        with open(tokenized_path, mode="w", encoding="utf-8") as t:
            for line in f:
                words = wsplit(line)
                tokens = [dictionary.index(w) if w in dictionary else UNKNOWN for w in words]
                t.write(" ".join([str(_t) for _t in tokens]) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility Parser")
    parser.add_argument("path", type=str, help="target path")
    parser.add_argument("--extract", action="store_const", const=True, default=False, help="extract abstract xml")
    parser.add_argument("--wakati", action="store_const", const=True, default=False, help="separate japanese text (You need janome)")
    parser.add_argument("--concat", type=str, help="concatenate files that matches the pattern in target directory")
    parser.add_argument("--tokenize", type=int, default=-1, help="make vocab file and tokenize target file. vocab size is directed size. (You need MeCab)")

    args = parser.parse_args()
    path = args.path
    if path.startswith("/"):
        path = os.path.join(os.path.dirname(__file__), path)

    if args.extract:
        extract(path)
    elif args.wakati:
        wakati(path)
    elif args.concat:
        concat(path, args.concat)
    elif args.tokenize > 0:
        tokenize(path, args.tokenize)
