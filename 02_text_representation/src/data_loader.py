from pathlib import Path
from typing import Tuple, List
import numpy as np


def load_text_files(data_dir: str, category: str, split: str = 'train') -> List[str]:
    """
    Load all text files from one category
    
    Args:
        data_dir: Directory containing data (e.g., 'data')
        category: Category name ('thoisu', 'kinhte', 'congnghe')
        split: 'train' or 'test'
        
    Returns:
        List of text contents
    """
    category_path = Path(data_dir) / split / category
    texts = []
    
    if not category_path.exists():
        print(f"Warning: {category_path} does not exist!")
        return texts
    
    # Đọc tất cả file .txt
    for file_path in sorted(category_path.glob('*.txt')):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # Chỉ thêm nếu không rỗng
                    texts.append(content)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return texts


def load_dataset(data_dir: str = 'data') -> Tuple[List[str], np.ndarray, List[str], np.ndarray]:
    """
    Load entire dataset (train and test)
    
    Args:
        data_dir: Directory containing data
        
    Returns:
        X_train: List of train texts
        y_train: Array of train labels
        X_test: List of test texts
        y_test: Array of test labels
    """
    categories = ['thoisu', 'kinhte', 'congnghe']
    category_to_id = {cat: idx for idx, cat in enumerate(categories)}
    
    X_train, y_train = [], []
    X_test, y_test = [], []
    
    # Load train data
    print("Loading training data...")
    for category in categories:
        texts = load_text_files(data_dir, category, 'train')
        X_train.extend(texts)
        y_train.extend([category_to_id[category]] * len(texts))
        print(f"  - {category}: {len(texts)} samples")
    
    # Load test data
    print("\nLoading test data...")
    for category in categories:
        texts = load_text_files(data_dir, category, 'test')
        X_test.extend(texts)
        y_test.extend([category_to_id[category]] * len(texts))
        print(f"  - {category}: {len(texts)} samples")
    
    # Convert to numpy array
    y_train = np.array(y_train)
    y_test = np.array(y_test)
    
    print(f"\nSummary:")
    print(f"  Train: {len(X_train)} samples")
    print(f"  Test: {len(X_test)} samples")
    print(f"  Categories: {categories}")
    
    return X_train, y_train, X_test, y_test


def get_category_names() -> List[str]:
    """Return list of category names"""
    return ['thoisu', 'kinhte', 'congnghe']


if __name__ == "__main__":
    # Test data loader
    X_train, y_train, X_test, y_test = load_dataset('data')
    
    print("\n" + "="*60)
    print("First text example:")
    print("="*60)
    print(f"Label: {y_train[0]} ({get_category_names()[y_train[0]]})")
    print(f"Content preview: {X_train[0][:200]}...")
