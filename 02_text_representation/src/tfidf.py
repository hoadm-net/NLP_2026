import numpy as np
from typing import List
from collections import Counter
from underthesea import word_tokenize


class TFIDF:
    """
    Manual TF-IDF (Term Frequency - Inverse Document Frequency)
    
    TF-IDF = TF * IDF
    - TF: Term frequency in document
    - IDF: log(N / df) - Measures word importance in corpus
    """
    
    def __init__(self, max_features: int = None, min_df: int = 1):
        """
        Args:
            max_features: Maximum number of features
            min_df: Minimum document frequency
        """
        self.max_features = max_features
        self.min_df = min_df
        self.vocabulary = {}  # {word: index}
        self.idf = None  # IDF values
        self.vocab_size = 0
        
    def fit(self, texts: List[str]):
        """
        Calculate IDF for each word in vocabulary
        
        Args:
            texts: List of texts
        """
        N = len(texts)  # Tổng số documents
        
        # Đếm document frequency
        doc_freq = Counter()
        word_counts = Counter()  # Để lọc theo max_features
        
        for text in texts:
            tokens = word_tokenize(text.lower(), format="text").split()
            word_counts.update(tokens)
            # Mỗi document chỉ đếm 1 lần
            doc_freq.update(set(tokens))
        
        # Lọc từ theo min_df
        valid_words = [word for word, freq in doc_freq.items() if freq >= self.min_df]
        
        # Lọc theo max_features
        if self.max_features and len(valid_words) > self.max_features:
            valid_words = sorted(valid_words, key=lambda w: word_counts[w], reverse=True)
            valid_words = valid_words[:self.max_features]
        
        # Tạo vocabulary
        self.vocabulary = {word: idx for idx, word in enumerate(sorted(valid_words))}
        self.vocab_size = len(self.vocabulary)
        
        # Tính IDF: log(N / df)
        self.idf = np.zeros(self.vocab_size)
        for word, idx in self.vocabulary.items():
            df = doc_freq[word]
            # Thêm smoothing: log((N + 1) / (df + 1)) + 1
            self.idf[idx] = np.log((N + 1) / (df + 1)) + 1
        
        print(f"TF-IDF fitted with vocabulary size: {self.vocab_size}")
        
    def transform(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """
        Convert texts to TF-IDF vectors
        
        Args:
            texts: List of texts
            normalize: Whether to normalize with L2 norm
            
        Returns:
            Matrix shape (n_texts, vocab_size)
        """
        result = np.zeros((len(texts), self.vocab_size))
        
        for i, text in enumerate(texts):
            tokens = word_tokenize(text.lower(), format="text").split()
            token_counts = Counter(tokens)
            
            # Tính TF
            total_words = len(tokens)
            if total_words == 0:
                continue
                
            for token, count in token_counts.items():
                if token in self.vocabulary:
                    idx = self.vocabulary[token]
                    # TF = count / total_words
                    tf = count / total_words
                    # TF-IDF = TF * IDF
                    result[i, idx] = tf * self.idf[idx]
            
            # L2 normalization
            if normalize:
                norm = np.linalg.norm(result[i])
                if norm > 0:
                    result[i] = result[i] / norm
        
        return result
    
    def fit_transform(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """Fit and transform in one step"""
        self.fit(texts)
        return self.transform(texts, normalize)
