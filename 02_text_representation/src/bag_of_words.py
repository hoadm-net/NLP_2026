import numpy as np
from typing import List
from collections import Counter
from underthesea import word_tokenize


class BagOfWords:
    """
    Manual Bag of Words (BoW)
    
    Represent text using word frequency vectors
    """
    
    def __init__(self, max_features: int = None, min_df: int = 1):
        """
        Args:
            max_features: Maximum number of features (keep most common words)
            min_df: Minimum document frequency (remove rare words)
        """
        self.max_features = max_features
        self.min_df = min_df
        self.vocabulary = {}  # {word: index}
        self.vocab_size = 0
        
    def fit(self, texts: List[str]):
        """
        Build vocabulary from corpus
        
        Args:
            texts: List of texts
        """
        # Đếm tần suất từ trong toàn bộ corpus
        word_counts = Counter()
        doc_freq = Counter()  # Số documents chứa từ
        
        for text in texts:
            tokens = word_tokenize(text.lower(), format="text").split()
            word_counts.update(tokens)
            # Đếm document frequency (mỗi doc chỉ đếm 1 lần)
            doc_freq.update(set(tokens))
        
        # Lọc từ theo min_df
        valid_words = [word for word, freq in doc_freq.items() if freq >= self.min_df]
        
        # Lọc theo max_features (giữ các từ phổ biến nhất)
        if self.max_features and len(valid_words) > self.max_features:
            # Sắp xếp theo tần suất giảm dần
            valid_words = sorted(valid_words, key=lambda w: word_counts[w], reverse=True)
            valid_words = valid_words[:self.max_features]
        
        # Tạo vocabulary
        self.vocabulary = {word: idx for idx, word in enumerate(sorted(valid_words))}
        self.vocab_size = len(self.vocabulary)
        
        print(f"Bag of Words fitted with vocabulary size: {self.vocab_size}")
        
    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Convert texts to BoW vectors
        
        Args:
            texts: List of texts
            
        Returns:
            Matrix shape (n_texts, vocab_size) with values as word frequencies
        """
        result = np.zeros((len(texts), self.vocab_size))
        
        for i, text in enumerate(texts):
            tokens = word_tokenize(text.lower(), format="text").split()
            # Đếm tần suất mỗi từ
            token_counts = Counter(tokens)
            
            for token, count in token_counts.items():
                if token in self.vocabulary:
                    idx = self.vocabulary[token]
                    result[i, idx] = count
        
        return result
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """Fit and transform in one step"""
        self.fit(texts)
        return self.transform(texts)
