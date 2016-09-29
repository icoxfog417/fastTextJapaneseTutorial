import os
import argparse
import numpy as np


def read_words_vector(path):
    vectors = {}
    with open(path, "r", encoding="utf-8") as vec:
        for i, line in enumerate(vec):
            try:
                elements = line.strip().split()
                word = elements[0]
                vec = np.array(elements[1:], dtype=float)
                if not word in vectors and len(vec) >= 100:
                    # ignore the case that vector size is invalid
                    vectors[word] = vec
            except ValueError:
                continue
            except UnicodeDecodeError:
                continue
    
    return vectors


def similarity(v1, v2):
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    return np.dot(v1, v2) / n1 / n2


def evaluate(path, word, negative, threshold):
    if not word:
        raise Exception("word is missing")

    vectors = read_words_vector(path)
    
    if word not in vectors:
        raise Exception("Sorry, this word is not registered in model.")

    w_vec = vectors[word]
    border_positive = threshold if threshold > 0 else 0.8
    border_negative = threshold if threshold > 0 else 0.3
    max_candidates = 15
    candidates = {}

    for w in vectors:
        try:
            if w_vec.shape != vectors[w].shape:
                raise Exception("size not match")
            s = similarity(w_vec, vectors[w])
        except Exception as ex:
            print(w + " is not valid word.")
            continue
        
        if negative and s <= border_negative:
            candidates[w] = s
            if len(candidates) % 5 == 0:
                border_negative -= 0.05
        elif not negative and s >= border_positive:
            candidates[w] = s
            if len(candidates) % 5 == 0:
                border_positive += 0.05
        
        if len(candidates) > max_candidates:
            break
    
    sorted_candidates = sorted(candidates, key=candidates.get, reverse=not negative)
    for c in sorted_candidates:
        print("{0}, {1}".format(c, candidates[c]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Fast Text")
    parser.add_argument("word", type=str, help="word to search similar words")
    parser.add_argument("--path", type=str, help="path to model file", default="")
    parser.add_argument("--negative", action="store_const", const=True, default=False, help="search opposite words")
    parser.add_argument("--threshold", "--t", dest="threshold", type=float, default=-1, help="threashold to judege similarity")

    args = parser.parse_args()
    path = args.path
    if not path:
        path = os.path.join(os.path.dirname(__file__), "fastText/model.vec")

    evaluate(path, args.word, args.negative, args.threshold)
