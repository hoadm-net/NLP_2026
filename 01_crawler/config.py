# URL gốc của Thanh Niên
BASE_URL = "https://thanhnien.vn"

# RSS Feeds cho các danh mục
RSS_FEEDS = {
    "thoisu": "https://thanhnien.vn/rss/thoi-su.rss",
    "kinhte": "https://thanhnien.vn/rss/kinh-te.rss",
    "congnghe": "https://thanhnien.vn/rss/cong-nghe.rss",
}

# Số lượng mẫu cho mỗi danh mục (FULL DATASET)
TRAIN_SAMPLES = {
    "thoisu": 800,
    "kinhte": 800,
    "congnghe": 200,
}

TEST_SAMPLES = {
    "thoisu": 200,
    "kinhte": 200,
    "congnghe": 50,
}

# Headers để giả lập trình duyệt
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Cấu hình crawl
DELAY_BETWEEN_REQUESTS = 1  # Giây giữa các request (tránh bị ban)
MAX_RETRIES = 3  # Số lần thử lại khi request thất bại
TIMEOUT = 30  # Timeout cho mỗi request (giây)

# Thư mục lưu dữ liệu
OUTPUT_DIR = "thanhnien"
DB_FILE = "thanhnien_urls.db"
TRAIN_DIR = "train"
TEST_DIR = "test"

# Cấu hình logging
LOG_FILE = "crawler.log"
LOG_LEVEL = "INFO"
