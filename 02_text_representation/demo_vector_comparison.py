import argparse
import numpy as np
from src import OneHotEncoder, BagOfWords, TFIDF


# Corpus mẫu để demo
CORPUS = [
    "AI và machine learning đang phát triển",
    "Machine learning là một phần của AI",
    "Deep learning là machine learning nâng cao",
]


def print_corpus():
    """Print corpus to screen"""
    print("\n" + "="*60)
    print("CORPUS")
    print("="*60)
    for i, text in enumerate(CORPUS, 1):
        print(f"Doc {i}: {text}")
    print("="*60 + "\n")


def demo_bow():
    """Demo Bag of Words - Print first sentence and corresponding vector"""
    print("\n" + "="*60)
    print("BAG OF WORDS DEMO")
    print("="*60)
    
    # Fit trên toàn bộ corpus
    bow = BagOfWords()
    X = bow.fit_transform(CORPUS)
    
    # In thông tin về câu đầu tiên
    first_sentence = CORPUS[0]
    first_vector = X[0]
    
    print(f"\nFirst sentence: \"{first_sentence}\"")
    print(f"\nVocabulary size: {bow.vocab_size}")
    print(f"Vocabulary: {sorted(bow.vocabulary.keys())}")
    
    print(f"\nVector representation (shape: {first_vector.shape}):")
    print(first_vector)
    
    # In các từ có giá trị > 0 với frequency
    print(f"\nWords in sentence with frequencies:")
    vocab_inv = {v: k for k, v in bow.vocabulary.items()}
    for idx in range(len(first_vector)):
        if first_vector[idx] > 0:
            print(f"  '{vocab_inv[idx]}': {first_vector[idx]:.0f}")
    
    print(f"\nMatrix for entire corpus (shape: {X.shape}):")
    print(X)
    print("="*60 + "\n")


def demo_tfidf():
    """Demo TF-IDF - Print first sentence and corresponding vector"""
    print("\n" + "="*60)
    print("TF-IDF DEMO")
    print("="*60)
    
    # Fit trên toàn bộ corpus
    tfidf = TFIDF()
    X = tfidf.fit_transform(CORPUS)
    
    # In thông tin về câu đầu tiên
    first_sentence = CORPUS[0]
    first_vector = X[0]
    
    print(f"\nFirst sentence: \"{first_sentence}\"")
    print(f"\nVocabulary size: {tfidf.vocab_size}")
    print(f"Vocabulary: {sorted(tfidf.vocabulary.keys())}")
    
    print(f"\nVector representation (shape: {first_vector.shape}):")
    print(first_vector)
    
    # In các từ có giá trị > 0 với TF-IDF score
    print(f"\nWords in sentence with TF-IDF scores:")
    vocab_inv = {v: k for k, v in tfidf.vocabulary.items()}
    for idx in range(len(first_vector)):
        if first_vector[idx] > 0:
            print(f"  '{vocab_inv[idx]}': {first_vector[idx]:.4f}")
    
    print(f"\nMatrix for entire corpus (shape: {X.shape}):")
    print(X)
    print("="*60 + "\n")


def demo_onehot():
    """Demo One-Hot Encoding - Print first sentence and corresponding vector"""
    print("\n" + "="*60)
    print("ONE-HOT ENCODING DEMO")
    print("="*60)
    
    # Fit trên toàn bộ corpus
    ohe = OneHotEncoder()
    X = ohe.fit_transform(CORPUS)
    
    # In thông tin về câu đầu tiên
    first_sentence = CORPUS[0]
    first_vector = X[0]
    
    print(f"\nFirst sentence: \"{first_sentence}\"")
    print(f"\nVocabulary size: {ohe.vocab_size}")
    print(f"Vocabulary: {sorted(ohe.vocabulary.keys())}")
    
    print(f"\nVector representation (shape: {first_vector.shape}):")
    print(first_vector)
    
    # In các từ có giá trị = 1
    print(f"\nWords in sentence (binary):")
    vocab_inv = {v: k for k, v in ohe.vocabulary.items()}
    for idx in range(len(first_vector)):
        if first_vector[idx] == 1:
            print(f"  '{vocab_inv[idx]}': {first_vector[idx]:.0f}")
    
    print(f"\nMatrix for entire corpus (shape: {X.shape}):")
    print(X)
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Demo text representation methods"
    )
    
    # Các tùy chọn (exclusive - chỉ chọn 1)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--print-corpus",
        action="store_true",
        help="Print corpus to screen"
    )
    group.add_argument(
        "--bow",
        action="store_true",
        help="Demo Bag of Words"
    )
    group.add_argument(
        "--tfidf",
        action="store_true",
        help="Demo TF-IDF"
    )
    group.add_argument(
        "--onehot",
        action="store_true",
        help="Demo One-Hot Encoding"
    )
    
    args = parser.parse_args()
    
    # Nếu không có tham số nào, in corpus
    if not (args.print_corpus or args.bow or args.tfidf or args.onehot):
        print_corpus()
    elif args.print_corpus:
        print_corpus()
    elif args.bow:
        demo_bow()
    elif args.tfidf:
        demo_tfidf()
    elif args.onehot:
        demo_onehot()


if __name__ == "__main__":
    main()
