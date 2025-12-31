# Thanh Niên Crawler

Thu thập dữ liệu bài viết từ [Thanh Niên](https://thanhnien.vn/) để phân loại văn bản.

## Mục tiêu

Xây dựng dataset từ 3 chủ đề:
- **Thời sự**: 1000 mẫu (800 train + 200 test)
- **Kinh tế**: 1000 mẫu (800 train + 200 test)
- **Công nghệ**: 250 mẫu (200 train + 50 test)

**Tổng: 2250 bài viết**

## Cấu trúc

```
01_crawler/
├── config.py                 # Cấu hình RSS feeds, số lượng mẫu
├── src/                      # Helper modules
│   ├── logger_utils.py
│   ├── file_utils.py
│   ├── database.py
│   ├── url_collector.py
│   └── article_crawler.py
├── collect_urls.py           # Thu thập URLs từ RSS
├── crawl_articles.py         # Crawl nội dung bài viết
├── thanhnien_crawler.py      # Pipeline hoàn chỉnh
└── thanhnien/                # Output dataset
    ├── train/
    │   ├── thoisu/
    │   ├── kinhte/
    │   └── congnghe/
    └── test/
        ├── thoisu/
        ├── kinhte/
        └── congnghe/
```

## Cài đặt

```bash
cd 01_crawler
pip install -r requirements.txt
```

## Sử dụng

### Cách 1: Chạy toàn bộ

```bash
python thanhnien_crawler.py
```

### Cách 2: Chạy từng bước

```bash
# Bước 1: Thu thập URLs
python collect_urls.py

# Bước 2: Crawl nội dung
python crawl_articles.py
```

### Options

```bash
# Chỉ thu thập URLs
python thanhnien_crawler.py --collect-only

# Chỉ crawl articles
python thanhnien_crawler.py --crawl-only

# Xem thống kê
python thanhnien_crawler.py --stats

# Crawl theo category
python crawl_articles.py --category thoisu --split train

# Giới hạn số lượng
python crawl_articles.py --count 50
```

## Ý tưởng

### Thu thập URLs
- Parse RSS feeds để lấy danh sách bài viết
- Lưu metadata vào SQLite database
- Tránh duplicate URLs

### Crawl nội dung
- Extract tiêu đề, mô tả, nội dung chính
- Lưu thành file `.txt` với format: `{category}_{index:04d}.txt`
- Theo dõi trạng thái crawl trong database

### Database tracking
- SQLite lưu trữ URL, category, trạng thái
- Cho phép pause/resume
- Tránh crawl trùng lặp
