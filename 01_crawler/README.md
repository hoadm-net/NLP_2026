# Thanh Niên Crawler - Topic Classification

Tool cào dữ liệu bài viết từ [Thanh Niên](https://thanhnien.vn/) để phân loại văn bản theo chủ đề (Topic Classification).

## Mục tiêu

Xây dựng bộ dữ liệu từ Thanh Niên với 3 danh mục chính sử dụng RSS feeds:
- **Thời sự**: https://thanhnien.vn/rss/thoi-su.rss
- **Kinh tế**: https://thanhnien.vn/rss/kinh-te.rss  
- **Công nghệ**: https://thanhnien.vn/rss/cong-nghe.rss

## Cấu trúc Dataset

```
thanhnien/
├── train/
│   ├── thoisu/      # 400 mẫu
│   ├── kinhte/      # 400 mẫu
│   └── congnghe/    # 200 mẫu
└── test/
    ├── thoisu/      # 100 mẫu
    ├── kinhte/      # 100 mẫu
    └── congnghe/    # 50 mẫu
```

**Tổng: 1250 bài viết** (1000 train + 250 test)

## Cấu trúc thư mục

```
crawler/
├── README.md                 # Tài liệu hướng dẫn
├── requirements.txt          # Các thư viện cần thiết
├── config.py                 # File cấu hình
├── utils.py                  # Các hàm tiện ích
├── collect_urls.py           # Script 1: Thu thập URLs từ RSS
├── crawl_articles.py         # Script 2: Crawl nội dung bài viết
├── thanhnien_urls.db         # SQLite database chứa URLs
└── thanhnien/                # Thư mục chứa dataset
    ├── train/
    └── test/
```

## Cài đặt

### 1. Cài đặt các thư viện

```bash
pip install -r requirements.txt
```

### 2. Kiểm tra cấu hình

Mở file [config.py](config.py) và điều chỉnh các thông số nếu cần:
- `RSS_FEEDS`: Các RSS feeds cho từng danh mục
- `TRAIN_SAMPLES`: Số lượng mẫu train cho mỗi danh mục
- `TEST_SAMPLES`: Số lượng mẫu test cho mỗi danh mục
- `DELAY_BETWEEN_REQUESTS`: Thời gian chờ giữa các request (mặc định: 2 giây)

## Quy trình sử dụng

### Bước 1: Thu thập URLs từ RSS

```bash
python collect_urls.py
```

Script này sẽ:
- Parse RSS feeds từ 3 danh mục
- Trích xuất URL, tiêu đề, mô tả, ngày đăng
- Lưu vào SQLite database (`thanhnien_urls.db`)
- Hiển thị thống kê số lượng bài viết thu thập được

**Output:**
```
==============================================================
Thanh Niên URL Collector - Thu thập URLs từ RSS
==============================================================

Thu thập RSS feeds: 100%|████████████| 3/3

==============================================================
Thống kê Database:1500

Phân bố theo danh mục:
  - thoisu: 500
  - kinhte: 500
  - congnghe: 50
  - kinhte: 150
  - congnghe: 150

Đã crawl: 0
Đã sử dụng trong dataset: 0
```

### Bước 2: Crawl nội dung bài viết

```bash
python crawl_articles.py
```

Script này sẽ:
- Đọc URLs từ database
- Crawl nội dung đầy đủ của từng bài viết
- Lưu vào folder structure theo train/test
- Các bài viết được sắp xếp theo thứ tự thời gian đăng
- Đánh dấu bài viết đã sử dụng trong database

**Output:**
```
==============================================================
Thanh Niên Article Crawler - Crawl nội dung bài viết
==============================================================

Crawling thoisu: 100%|████████████| 500/500
Crawling kinhte: 100%|████████████| 500/500
Crawling congnghe: 100%|██████████| 250/250

==============================================================
Kết quả crawl:
==============================================================

thoisu:
  Train: 400/400
  Test: 100/100

kinhte:
  Train: 400/400
  Test: 100/100

congnghe:
  Train: 200/200
  Test: 50/50

==============================================================
Thống kê Dataset:
==============================================================

Train:
  thoisu: 400 files
  kinhte: 400 files
  congnghe: 200 files

Test:
  thoisu: 100 files
  kinhte: 100 files
  congnghe: 50 files

Tổng: 1250 files (Train: 1000, Test: 250)
```

## Cấu trúc file dữ liệu

Mỗi file `.txt` chứa nội dung đầy đủ của bài viết:
- Tiêu đề
- Mô tả
- Nội dung chính

Tên file có dạng: `{category}_{index:04d}.txt`

Ví dụ:
- `thoisu_0001.txt`
- `kinhte_0042.txt`
- `congnghe_0150.txt`

## Đặc điểm của Dataset

### 1. Trộn lẫn theo thời gian
Các bài viết được sắp xếp theo thứ tự thời gian đăng bài (từ cũ đến mới), đảm bảo:
- Không có bias về thời gian
- Phân phối tự nhiên theo topic
- Phù hợp cho training model

### 2. Phân chia Train/Test
- **Train**: 80% dữ liệu (1000 mẫu)
  - Thời sự: 400 mẫu (40%)
  - Kinh tế: 400 mẫu (40%)
  - Công nghệ: 200 mẫu (20%)

- **Test**: 20% dữ liệu (250 mẫu)
  - Thời sự: 100 mẫu (40%)
  - Kinh tế: 100 mẫu (40%)
  - Công nghệ: 50 mẫu (20%)

### 3. Database tracking
- SQLite database lưu trữ metadata của tất cả bài viết
- Theo dõi trạng thái crawl và sử dụng
- Tránh duplicate khi chạy lại

## Tùy chỉnh

### Thay đổi số lượng mẫu

Chỉnh sửa trong [config.py](config.py):

```python
# Số lượng mẫu cho mỗi danh mục
TRAIN_SAMPLES = {
    "thoisu": 400,
    "kinhte": 400,
    "congnghe": 200,
}

TEST_SAMPLES = {
    "thoisu": 100,
    "kinhte": 100,
    "congnghe": 50,
}
```

### Thu thập thêm URLs

Chạy lại `collect_urls.py` để cập nhật database với các bài viết mới từ RSS:

```bash
python collect_urls.py
```

Database sẽ tự động bỏ qua các URL đã tồn tại.

### Crawl thêm dữ liệu

Nếu cần crawl thêm (ví dụ khi có bài viết mới trong database):

```bash
python crawl_articles.py
```

Script sẽ chỉ crawl các bài viết chưa được sử dụng (`used_in_dataset = 0`).

## Xử lý lỗi

### Lỗi: Database không tồn tại

```
Lỗi: Database không tồn tại: thanhnien_urls.db
Vui lòng chạy collect_urls.py trước!
```

**Giải pháp**: Chạy `python collect_urls.py` trước.

### Lỗi: Không đủ bài viết

```
Không đủ bài viết trong database. Cần: 500, Có: 300
```

**Giải pháp**: 
1. Chạy lại `collect_urls.py` sau vài ngày khi RSS feeds cập nhật bài mới
2. Điều chỉnh số lượng mẫu trong `config.py` cho phù hợp với số URLs có sẵn
3. Chấp nhận dataset nhỏ hơn và chia lại tỷ lệ train/test

**Giới hạn của RSS**: RSS feeds thường chỉ cung cấp 300-500 bài viết gần nhất. Để có nhiều dữ liệu hơn, cần chạy `collect_urls.py` định kỳ để tích lũy URLs theo thời gian.

### Lỗi: Connection timeout

**Giải pháp**: Tăng `TIMEOUT` và `DELAY_BETWEEN_REQUESTS` trong [config.py](config.py)

### Lỗi: Rate limiting (429)

**Giải pháp**: Tăng `DELAY_BETWEEN_REQUESTS` lên 3-5 giây

## Xem thống kê Database

Bạn có thể xem trực tiếp database bằng SQLite client:

```bash
# Sử dụng sqlite3 command line
sqlite3 thanhnien_urls.db

# Xem tất cả bài viết
SELECT category, COUNT(*) FROM articles GROUP BY category;

# Xem bài viết đã crawl
SELECT COUNT(*) FROM articles WHERE crawled = 1;

# Xem bài viết đã dùng trong dataset
SELECT COUNT(*) FROM articles WHERE used_in_dataset = 1;
```

## Ứng dụng

Dataset này phù hợp cho các bài toán:

### 1. **Topic Classification** (Chính)
Phân loại văn bản vào 3 lớp: Thời sự, Kinh tế, Công nghệ

### 2. **Text Mining**
Khai thác thông tin, phân tích nội dung tin tức

### 3. **Named Entity Recognition (NER)**
Nhận dạng các thực thể (người, địa điểm, tổ chức)

### 4. **Sentiment Analysis**
Phân tích quan điểm, cảm xúc trong tin tức

### 5. **Text Summarization**
Tóm tắt nội dung bài viết

## Disclaimer

Tool này chỉ dành cho mục đích học tập và nghiên cứu. Vui lòng tuân thủ điều khoản sử dụng của Thanh Niên.
