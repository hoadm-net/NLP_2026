"""
Script 1: Thu thập URLs từ RSS feeds và lưu vào SQLite
"""

import requests
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import logging
from tqdm import tqdm

import config
from utils import setup_logger


class URLCollector:
    """Thu thập URLs từ RSS feeds"""
    
    def __init__(self):
        self.logger = setup_logger()
        self.db_file = config.DB_FILE
        self.setup_database()
        
    def setup_database(self):
        """Tạo database và bảng nếu chưa tồn tại"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                category TEXT NOT NULL,
                published_date TEXT,
                description TEXT,
                collected_at TEXT,
                crawled INTEGER DEFAULT 0,
                used_in_dataset INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info(f"Database đã sẵn sàng: {self.db_file}")
    
    def parse_rss(self, rss_url, category):
        """
        Parse RSS feed và trích xuất thông tin bài viết
        
        Args:
            rss_url: URL của RSS feed
            category: Danh mục (thoisu, kinhte, congnghe)
            
        Returns:
            List các dictionary chứa thông tin bài viết
        """
        try:
            response = requests.get(rss_url, headers=config.HEADERS, timeout=config.TIMEOUT)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            articles = []
            
            # Tìm tất cả các items trong channel
            for item in root.findall('.//item'):
                article = {
                    'category': category,
                    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Title
                title = item.find('title')
                article['title'] = title.text if title is not None else ''
                
                # Link/URL
                link = item.find('link')
                article['url'] = link.text if link is not None else ''
                
                # Description
                description = item.find('description')
                article['description'] = description.text if description is not None else ''
                
                # Published date
                pub_date = item.find('pubDate')
                if pub_date is not None:
                    # Parse RFC 2822 date format
                    try:
                        dt = datetime.strptime(pub_date.text, '%a, %d %b %Y %H:%M:%S %z')
                        article['published_date'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        article['published_date'] = pub_date.text
                else:
                    article['published_date'] = ''
                
                if article['url']:
                    articles.append(article)
            
            self.logger.info(f"Đã parse {len(articles)} bài viết từ {category}")
            return articles
            
        except Exception as e:
            self.logger.error(f"Lỗi khi parse RSS {rss_url}: {e}")
            return []
    
    def save_to_database(self, articles):
        """
        Lưu danh sách bài viết vào database
        
        Args:
            articles: List các dictionary chứa thông tin bài viết
            
        Returns:
            Số lượng bài viết mới được thêm vào
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        new_count = 0
        duplicate_count = 0
        
        for article in articles:
            try:
                cursor.execute('''
                    INSERT INTO articles (url, title, category, published_date, description, collected_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    article['url'],
                    article['title'],
                    article['category'],
                    article['published_date'],
                    article['description'],
                    article['collected_at']
                ))
                new_count += 1
            except sqlite3.IntegrityError:
                # URL đã tồn tại
                duplicate_count += 1
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Đã thêm {new_count} bài viết mới, {duplicate_count} bài viết trùng")
        return new_count
    
    def collect_all(self):
        """Thu thập URLs từ tất cả RSS feeds"""
        total_new = 0
        
        for category, rss_url in tqdm(config.RSS_FEEDS.items(), desc="Thu thập RSS feeds"):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Đang thu thập: {category}")
            self.logger.info(f"RSS URL: {rss_url}")
            
            articles = self.parse_rss(rss_url, category)
            new_count = self.save_to_database(articles)
            total_new += new_count
            
            # Delay giữa các request
            time.sleep(config.DELAY_BETWEEN_REQUESTS)
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Tổng số bài viết mới: {total_new}")
        
        return total_new
    
    def get_statistics(self):
        """Lấy thống kê database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Tổng số bài viết
        cursor.execute('SELECT COUNT(*) FROM articles')
        total = cursor.fetchone()[0]
        
        # Số bài viết theo danh mục
        cursor.execute('SELECT category, COUNT(*) FROM articles GROUP BY category')
        by_category = dict(cursor.fetchall())
        
        # Số bài viết đã crawl
        cursor.execute('SELECT COUNT(*) FROM articles WHERE crawled = 1')
        crawled = cursor.fetchone()[0]
        
        # Số bài viết đã dùng trong dataset
        cursor.execute('SELECT COUNT(*) FROM articles WHERE used_in_dataset = 1')
        used = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'by_category': by_category,
            'crawled': crawled,
            'used_in_dataset': used
        }


def main():
    """Hàm chính"""
    print("="*60)
    print("Thanh Niên URL Collector - Thu thập URLs từ RSS")
    print("="*60)
    
    collector = URLCollector()
    
    # Thu thập URLs
    print("\nBắt đầu thu thập URLs từ RSS feeds...")
    new_count = collector.collect_all()
    
    # Hiển thị thống kê
    print("\n" + "="*60)
    print("Thống kê Database:")
    print("="*60)
    stats = collector.get_statistics()
    print(f"Tổng số bài viết: {stats['total']}")
    print(f"\nPhân bố theo danh mục:")
    for category, count in stats['by_category'].items():
        print(f"  - {category}: {count}")
    print(f"\nĐã crawl: {stats['crawled']}")
    print(f"Đã sử dụng trong dataset: {stats['used_in_dataset']}")
    
    print("\n" + "="*60)
    print(f"Hoàn tất! Database: {collector.db_file}")
    print("="*60)


if __name__ == "__main__":
    main()
