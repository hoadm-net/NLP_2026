# Bài 02: Biểu diễn văn bản (Text Representation)

## 📖 Mục tiêu

Học cách chuyển đổi văn bản thành vector số để máy tính có thể xử lý. Bài tập này sẽ giúp bạn:

- Hiểu các kỹ thuật biểu diễn văn bản cơ bản
- Implement **thủ công** các phương pháp: One-Hot Encoding, Bag of Words (BoW), TF-IDF
- Tokenization sử dụng thư viện [underthesea](https://github.com/undertheseanlp/underthesea)
- So sánh kết quả thủ công với thư viện sklearn
- Áp dụng các mô hình machine learning để phân loại văn bản

## 📊 Dữ liệu

Sử dụng dataset từ [Bài 01](../01_crawler/) gồm 3 chủ đề:
- **Thời sự** (thoisu)
- **Kinh tế** (kinhte)  
- **Công nghệ** (congnghe)

```
data/
├── train/
│   ├── thoisu/
│   ├── kinhte/
│   └── congnghe/
└── test/
    ├── thoisu/
    ├── kinhte/
    └── congnghe/
```

## 📚 Nội dung bài học

### 1. One-Hot Encoding
- Binary representation: 1 nếu từ xuất hiện, 0 nếu không
- Implement thủ công từ đầu
- Đơn giản nhưng vector rất lớn và sparse

### 2. Bag of Words (BoW)
- Đếm tần suất xuất hiện của từ
- Xây dựng vocabulary từ corpus
- Hỗ trợ `max_features` và `min_df`

### 3. TF-IDF
- Term Frequency - Inverse Document Frequency
- Nhấn mạnh từ quan trọng, giảm ảnh hưởng từ phổ biến
- Công thức: TF-IDF = TF * IDF
- L2 normalization

### 4. Text Classification
Sử dụng 2 mô hình:
- **Logistic Regression**: Linear classifier hiệu quả
- **Multinomial Naive Bayes**: Phù hợp với text classification

## 📂 Cấu trúc thư mục

```
02_text_representation/
├── README.md                        # Hướng dẫn
├── requirements.txt                 # Dependencies
├── data/                            # Dataset từ bài 01
│   ├── train/
│   │   ├── congnghe/
│   │   ├── kinhte/
│   │   └── thoisu/
│   └── test/
│       ├── congnghe/
│       ├── kinhte/
│       └── thoisu/
├── src/
│   ├── __init__.py                  # Package exports
│   ├── data_loader.py               # Load train/test data
│   ├── one_hot_encoder.py           # One-Hot Encoding implementation
│   ├── bag_of_words.py              # Bag of Words implementation
│   └── tfidf.py                     # TF-IDF implementation
├── demo_vector_comparison.py        # Demo các phương pháp biểu diễn
├── compare_with_sklearn.py          # So sánh với sklearn
└── text_classification.py           # Phân loại văn bản
```

## 🚀 Hướng dẫn sử dụng

### 1. Cài đặt

```bash
cd 02_text_representation

# Tạo virtual environment (khuyến nghị Python 3.11)
python3.11 -m venv ../.venv
source ../.venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2. Demo các phương pháp biểu diễn

```bash
# In corpus mẫu
python demo_vector_comparison.py

# Demo One-Hot Encoding
python demo_vector_comparison.py --onehot

# Demo Bag of Words
python demo_vector_comparison.py --bow

# Demo TF-IDF
python demo_vector_comparison.py --tfidf
```

### 3. So sánh với sklearn

```bash
# So sánh Bag of Words
python compare_with_sklearn.py --compare bow

# So sánh TF-IDF
python compare_with_sklearn.py --compare tfidf
```

### 4. Phân loại văn bản

**Chọn phương pháp biểu diễn và mô hình:**

```bash
# BoW + Logistic Regression
python text_classification.py -r bow -clf lr

# TF-IDF + Naive Bayes
python text_classification.py -r tfidf -clf nb

# One-Hot + Naive Bayes
python text_classification.py -r onehot -clf nb
```

**So sánh tất cả các phương pháp:**

```bash
# So sánh với Logistic Regression
python text_classification.py --compare -clf lr

# So sánh với Naive Bayes
python text_classification.py --compare -clf nb
```

**Output:**
- Accuracy trên tập test
- Classification report (precision, recall, f1-score)
- Confusion matrix

## 📊 Kết quả thực nghiệm

### So sánh implementation thủ công vs sklearn

| Phương pháp | Manual | Sklearn | Khác biệt |
|-------------|--------|---------|-----------|
| Bag of Words | ✅ | ✅ | Identical |
| TF-IDF | ✅ | ✅ | Slightly different (IDF formula) |

**Note**: TF-IDF có chút khác biệt do công thức IDF:
- Manual: `log((N+1)/(df+1)) + 1`
- Sklearn: `log((N+1)/(df+1))`

### Performance classification

| Representation | Classifier | Test Accuracy | Features |
|----------------|------------|---------------|----------|
| Bag of Words | Logistic Regression | ~85-90% | ~10000+ |
| TF-IDF | Logistic Regression | ~87-92% | ~10000+ |
| TF-IDF | Naive Bayes | ~85-89% | ~10000+ |
| One-Hot | Naive Bayes | ~80-85% | ~10000+ |

**Best combination**: TF-IDF + Logistic Regression

## 🎯 Tính năng chính

### ✅ Đã hoàn thành

1. **One-Hot Encoding** (`src/one_hot_encoder.py`)
   - Binary vector representation
   - Vocabulary building
   - fit/transform/fit_transform methods

2. **Bag of Words** (`src/bag_of_words.py`)
   - Frequency-based representation
   - Support for `max_features` and `min_df`
   - Document frequency filtering

3. **TF-IDF** (`src/tfidf.py`)
   - Term Frequency - Inverse Document Frequency
   - IDF calculation with smoothing
   - L2 normalization

4. **Data Loader** (`src/data_loader.py`)
   - Load train/test split
   - Category mapping
   - Batch processing

5. **Comparison Tools**
   - `demo_vector_comparison.py`: Visualize vector differences
   - `compare_with_sklearn.py`: Validate manual implementations

6. **Text Classification** (`text_classification.py`)
   - Multiple representation methods
   - Two classifiers: LR and NB
   - Full evaluation metrics
   - Comparison mode

