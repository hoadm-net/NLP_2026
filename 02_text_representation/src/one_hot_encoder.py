import numpy as np
from typing import List
from underthesea import word_tokenize


class OneHotEncoder:
    """
    Manual One-Hot Encoding
    
    Each word in vocabulary is represented by a binary vector
    with one value as 1, rest are 0
    """
    
    def __init__(self):
        self.vocabulary = {}  # {word: index}
        self.vocab_size = 0
        
    def fit(self, texts: List[str]):
        """
        Build vocabulary from corpus
        
        Args:
            texts: List of texts
        """
        # Thu thập tất cả các từ unique
        all_words = set()
        for text in texts:
            tokens = word_tokenize(text.lower(), format="text").split()
            all_words.update(tokens)
        
        # Tạo mapping từ word -> index
        self.vocabulary = {word: idx for idx, word in enumerate(sorted(all_words))}
        self.vocab_size = len(self.vocabulary)
        
        print(f"One-Hot Encoder fitted with vocabulary size: {self.vocab_size}")
        
    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Convert texts to one-hot vectors
        
        Args:
            texts: List of texts
            
        Returns:
            Matrix shape (n_texts, vocab_size)
        """
        result = np.zeros((len(texts), self.vocab_size))
        
        for i, text in enumerate(texts):
            tokens = word_tokenize(text.lower(), format="text").split()
            for token in tokens:
                if token in self.vocabulary:
                    idx = self.vocabulary[token]
                    result[i, idx] = 1  # Đánh dấu từ xuất hiện
        
        return result
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """Fit and transform in one step"""
        self.fit(texts)
        return self.transform(texts)
