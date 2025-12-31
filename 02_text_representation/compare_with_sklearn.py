import argparse
import numpy as np
import os
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from underthesea import word_tokenize
from src import BagOfWords, TFIDF


def underthesea_tokenizer(text):
    """Custom tokenizer using underthesea for sklearn"""
    return word_tokenize(text.lower(), format="text").split()


def load_train_data(data_dir="data/train", max_files_per_category=50):
    """Load data from train directory
    
    Args:
        data_dir: Path to train directory
        max_files_per_category: Maximum number of files per category to avoid too much data
    
    Returns:
        texts: List of texts
        labels: List of corresponding labels
    """
    texts = []
    labels = []
    
    data_path = Path(data_dir)
    
    # Duyệt qua từng category
    for category_dir in sorted(data_path.iterdir()):
        if category_dir.is_dir():
            category_name = category_dir.name
            print(f"Loading {category_name}...", end=" ")
            
            # Đọc các file trong category
            files = sorted(list(category_dir.glob("*.txt")))[:max_files_per_category]
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read().strip()
                        if text:  # Chỉ thêm nếu không rỗng
                            texts.append(text)
                            labels.append(category_name)
                except Exception as e:
                    print(f"\nError reading {file_path}: {e}")
            
            print(f"{len(files)} files")
    
    print(f"\nTotal: {len(texts)} documents from {len(set(labels))} categories")
    return texts, labels


def compare_bow_values():
    """Compare specific values of Bag of Words"""
    print("="*80)
    print("COMPARE BAG OF WORDS VALUES")
    print("="*80)
    
    print("\nLoading train data...")
    texts, labels = load_train_data()
    
    # Manual implementation
    bow_manual = BagOfWords()
    X_bow = bow_manual.fit_transform(texts)
    
    # Sklearn implementation (sử dụng underthesea tokenizer)
    count_vec = CountVectorizer(tokenizer=underthesea_tokenizer, lowercase=False)
    X_count = count_vec.fit_transform(texts).toarray()
    
    print(f"\nExample first document: '{texts[0]}'")
    print(f"\nManual BoW - Top 5 words with counts:")
    manual_vocab_inv = {v: k for k, v in bow_manual.vocabulary.items()}
    top_indices = np.argsort(X_bow[0])[-5:][::-1]
    for idx in top_indices:
        if X_bow[0, idx] > 0:
            print(f"  '{manual_vocab_inv[idx]}': {X_bow[0, idx]:.0f}")
    
    print(f"\nSklearn CountVectorizer - Top 5 words with counts:")
    sklearn_vocab_inv = {v: k for k, v in count_vec.vocabulary_.items()}
    top_indices_sk = np.argsort(X_count[0])[-5:][::-1]
    for idx in top_indices_sk:
        if X_count[0, idx] > 0:
            print(f"  '{sklearn_vocab_inv[idx]}': {X_count[0, idx]:.0f}")
    
    print("\nEXPLANATION:")
    print("- Value = word frequency in document")  # Giá trị = số lần xuất hiện của từ trong document
    print("- Both use underthesea tokenizer")  # Cả 2 đều dùng underthesea tokenizer
    print("- Results MUST be the same if implementation is correct")  # Kết quả phải giống nhau nếu implementation đúng


def compare_tfidf_values():
    """Compare TF-IDF values"""
    print("="*80)
    print("COMPARE TF-IDF VALUES")
    print("="*80)
    
    print("\nLoading train data...")
    texts, labels = load_train_data()
    
    # Manual implementation
    tfidf_manual = TFIDF()
    X_tfidf = tfidf_manual.fit_transform(texts)
    
    # Sklearn implementation (sử dụng underthesea tokenizer)
    tfidf_vec = TfidfVectorizer(tokenizer=underthesea_tokenizer, lowercase=False)
    X_tfidf_sk = tfidf_vec.fit_transform(texts).toarray()
    
    print(f"\nExample first document: '{texts[0]}'")
    print(f"\nManual TFIDF - Top 5 words with scores:")
    manual_vocab_inv = {v: k for k, v in tfidf_manual.vocabulary.items()}
    top_indices = np.argsort(X_tfidf[0])[-5:][::-1]
    for idx in top_indices:
        if X_tfidf[0, idx] > 0:
            print(f"  '{manual_vocab_inv[idx]}': {X_tfidf[0, idx]:.4f}")
    
    print(f"\nSklearn TfidfVectorizer - Top 5 words with scores:")
    sklearn_vocab_inv = {v: k for k, v in tfidf_vec.vocabulary_.items()}
    top_indices_sk = np.argsort(X_tfidf_sk[0])[-5:][::-1]
    for idx in top_indices_sk:
        if X_tfidf_sk[0, idx] > 0:
            print(f"  '{sklearn_vocab_inv[idx]}': {X_tfidf_sk[0, idx]:.4f}")
    
    print("\nEXPLANATION:")
    print("- TF-IDF = TF * IDF")
    print("- TF: term frequency in document (normalized)")  # Tần suất từ trong document (đã normalize)
    print("- IDF: log((N+1)/(df+1)) + 1 (manual) vs log((N+1)/(df+1)) (sklearn)")
    print("- Values are L2 normalized to [0, 1]")  # Giá trị được L2 normalize về [0, 1]
    print("- Same tokenizer but IDF formula slightly different:")  # Cùng tokenizer nhưng công thức IDF hơi khác:
    print("  + Manual: log((N+1)/(df+1)) + 1")
    print("  + Sklearn: log((N+1)/(df+1))")
    print("- Therefore values differ slightly (but correlation is the same)")  # Do đó giá trị khác nhau một chút (nhưng tương quan giống nhau)


def main():
    """Main function - Compare manual implementation vs sklearn"""
    parser = argparse.ArgumentParser(
        description='Compare manual implementation vs sklearn for BoW and TF-IDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compare_with_sklearn.py --compare bow    # Compare Bag of Words
  python compare_with_sklearn.py --compare tfidf  # Compare TF-IDF
        """
    )
    
    parser.add_argument(
        '--compare', '-c',
        type=str,
        choices=['bow', 'tfidf'],
        required=True,
        help='Choose comparison type: bow or tfidf'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("COMPARE MANUAL IMPLEMENTATION VS SKLEARN")
    print("="*80 + "\n")
    
    if args.compare == 'bow':
        compare_bow_values()
    elif args.compare == 'tfidf':
        compare_tfidf_values()
    
    print("\nCompleted!\n")


if __name__ == "__main__":
    main()
