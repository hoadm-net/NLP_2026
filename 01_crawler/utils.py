"""
Các hàm tiện ích cho Thanh Niên Crawler
"""

import os
import json
import csv
import logging
from datetime import datetime
import config


def setup_logger():
    """
    Thiết lập logger để ghi log
    
    Returns:
        logging.Logger object
    """
    logger = logging.getLogger('ThanhNienCrawler')
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Tạo formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)
    
    file_handler = logging.FileHandler(
        os.path.join(config.OUTPUT_DIR, config.LOG_FILE),
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def create_output_dir():
    """Tạo thư mục output nếu chưa tồn tại"""
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)
        print(f"Đã tạo thư mục: {config.OUTPUT_DIR}")


def save_to_csv(articles, filepath):
    """
    Lưu dữ liệu vào file CSV
    
    Args:
        articles: List các dictionary chứa thông tin bài viết
        filepath: Đường dẫn file CSV
    """
    if not articles:
        return
    
    keys = articles[0].keys()
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(articles)
    
    print(f"Đã lưu {len(articles)} bài viết vào {filepath}")


def save_to_json(articles, filepath):
    """
    Lưu dữ liệu vào file JSON
    
    Args:
        articles: List các dictionary chứa thông tin bài viết
        filepath: Đường dẫn file JSON
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"Đã lưu {len(articles)} bài viết vào {filepath}")


def clean_text(text):
    """
    Làm sạch text
    
    Args:
        text: Chuỗi cần làm sạch
        
    Returns:
        Chuỗi đã được làm sạch
    """
    if not text:
        return ""
    
    # Loại bỏ khoảng trắng thừa
    text = ' '.join(text.split())
    
    # Loại bỏ các ký tự đặc biệt không mong muốn
    text = text.strip()
    
    return text


def format_date(date_string):
    """
    Chuẩn hóa định dạng ngày tháng
    
    Args:
        date_string: Chuỗi ngày tháng từ website
        
    Returns:
        Chuỗi ngày tháng định dạng chuẩn
    """
    # Implement logic để parse date từ Thanh Niên
    # Ví dụ: "27/12/2025 10:30 GMT+7"
    return date_string


def get_category_name(url):
    """
    Lấy tên danh mục từ URL
    
    Args:
        url: URL của bài viết
        
    Returns:
        Tên danh mục
    """
    for category, category_url in config.CATEGORIES.items():
        if category in url or url.startswith(category_url):
            return category
    return "unknown"
