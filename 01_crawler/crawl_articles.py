"""
Script 2: Crawl nội dung bài viết và lưu vào folder structure
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import time
import logging
from datetime import datetime
from tqdm import tqdm
import random

import config
from utils import setup_logger, clean_text


class ArticleCrawler:
    """Crawl nội dung bài viết từ database và lưu vào folder"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.logger = setup_logger()
        self.db_file = config.DB_FILE
        self.setup_folders()
        
    def setup_folders(self):
        """Tạo cấu trúc thư mục"""
        base_dir = config.OUTPUT_DIR
        
        # Train folders
        for category in config.TRAIN_SAMPLES.keys():
            train_path = os.path.join(base_dir, config.TRAIN_DIR, category)
            os.makedirs(train_path, exist_ok=True)
        
        # Test folders
        for category in config.TEST_SAMPLES.keys():
            test_path = os.path.join(base_dir, config.TEST_DIR, category)
            os.makedirs(test_path, exist_ok=True)
        
        self.logger.info(f"Đã tạo cấu trúc thư mục tại: {base_dir}")
    
    def get_page(self, url, retries=config.MAX_RETRIES):
        """Lấy nội dung trang web"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=config.TIMEOUT)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'lxml')
            except requests.RequestException as e:
                self.logger.warning(f"Lỗi khi truy cập {url} (lần {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(config.DELAY_BETWEEN_REQUESTS)
                else:
                    self.logger.error(f"Không thể truy cập {url} sau {retries} lần thử")
                    return None
    
    def extract_article_content(self, url):
        """
        Trích xuất nội dung bài viết
        
        Args:
            url: URL của bài viết
            
        Returns:
            String chứa nội dung bài viết hoặc None nếu thất bại
        """
        soup = self.get_page(url)
        if not soup:
            return None
        
        try:
            content_parts = []
            
            # Tiêu đề
            title_tag = soup.find('h1', class_='detail-title')
            if title_tag:
                title_span = title_tag.find('span', {'data-role': 'title'})
                if title_span:
                    content_parts.append(title_span.get_text(strip=True))
            
            # Mô tả/Sapo
            description_tag = soup.find('h2', class_='detail-sapo')
            if not description_tag:
                description_tag = soup.find('div', class_='detail-sapo')
            if description_tag:
                content_parts.append(description_tag.get_text(strip=True))
            
            # Nội dung chính
            content_div = soup.find('div', class_='detail-content')
            if not content_div:
                content_div = soup.find('div', id='main-detail-content')
            
            if content_div:
                paragraphs = content_div.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # Bỏ qua đoạn quá ngắn
                        content_parts.append(text)
            
            if content_parts:
                full_content = '\n\n'.join(content_parts)
                return clean_text(full_content)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất nội dung từ {url}: {e}")
            return None
    
    def get_articles_from_db(self, category, limit=None):
        """
        Lấy danh sách bài viết từ database
        
        Args:
            category: Danh mục cần lấy
            limit: Số lượng tối đa (None = lấy tất cả)
            
        Returns:
            List các tuple (id, url, published_date)
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, url, published_date 
            FROM articles 
            WHERE category = ? AND used_in_dataset = 0
            ORDER BY published_date DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (category,))
        articles = cursor.fetchall()
        
        conn.close()
        return articles
    
    def mark_as_used(self, article_id):
        """Đánh dấu bài viết đã được sử dụng trong dataset"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE articles 
            SET crawled = 1, used_in_dataset = 1
            WHERE id = ?
        ''', (article_id,))
        
        conn.commit()
        conn.close()
    
    def save_article(self, content, category, split, index):
        """
        Lưu bài viết vào file
        
        Args:
            content: Nội dung bài viết
            category: Danh mục (thoisu, kinhte, congnghe)
            split: train hoặc test
            index: Số thứ tự của file
        """
        folder = os.path.join(config.OUTPUT_DIR, split, category)
        filename = f"{category}_{index:04d}.txt"
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def crawl_category(self, category, train_count, test_count):
        """
        Crawl một danh mục với số lượng train và test xác định
        
        Args:
            category: Danh mục cần crawl
            train_count: Số lượng mẫu train
            test_count: Số lượng mẫu test
            
        Returns:
            Tuple (số lượng train thành công, số lượng test thành công)
        """
        total_needed = train_count + test_count
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Crawl danh mục: {category}")
        self.logger.info(f"Train: {train_count}, Test: {test_count}, Tổng: {total_needed}")
        
        # Lấy danh sách bài viết từ database (lấy nhiều hơn một chút để phòng trường hợp fail)
        articles = self.get_articles_from_db(category, limit=total_needed * 2)
        
        if len(articles) < total_needed:
            self.logger.warning(f"Không đủ bài viết trong database. Cần: {total_needed}, Có: {len(articles)}")
        
        # Trộn theo thứ tự thời gian (đã sort DESC trong query, giờ reverse để có thứ tự cũ -> mới)
        articles = list(reversed(articles))
        
        train_success = 0
        test_success = 0
        
        # Crawl từng bài viết
        for idx, (article_id, url, pub_date) in enumerate(tqdm(articles, desc=f"Crawling {category}")):
            if train_success >= train_count and test_success >= test_count:
                break
            
            # Crawl nội dung
            content = self.extract_article_content(url)
            
            if content:
                # Xác định split (train hoặc test)
                if train_success < train_count:
                    split = config.TRAIN_DIR
                    index = train_success + 1
                    train_success += 1
                elif test_success < test_count:
                    split = config.TEST_DIR
                    index = test_success + 1
                    test_success += 1
                else:
                    continue
                
                # Lưu file
                filepath = self.save_article(content, category, split, index)
                self.logger.info(f"Đã lưu: {filepath}")
                
                # Đánh dấu đã dùng
                self.mark_as_used(article_id)
            
            # Delay
            time.sleep(config.DELAY_BETWEEN_REQUESTS)
        
        self.logger.info(f"Hoàn tất {category}: Train={train_success}/{train_count}, Test={test_success}/{test_count}")
        return train_success, test_success
    
    def crawl_all(self):
        """Crawl tất cả các danh mục"""
        results = {}
        
        print("\n" + "="*60)
        print("Bắt đầu crawl tất cả danh mục")
        print("="*60)
        
        for category in config.TRAIN_SAMPLES.keys():
            train_count = config.TRAIN_SAMPLES[category]
            test_count = config.TEST_SAMPLES[category]
            
            train_success, test_success = self.crawl_category(
                category, 
                train_count, 
                test_count
            )
            
            results[category] = {
                'train': train_success,
                'test': test_success
            }
        
        return results
    
    def get_dataset_statistics(self):
        """Thống kê dataset đã tạo"""
        stats = {
            'train': {},
            'test': {}
        }
        
        for split in ['train', 'test']:
            for category in config.TRAIN_SAMPLES.keys():
                folder = os.path.join(config.OUTPUT_DIR, split, category)
                if os.path.exists(folder):
                    count = len([f for f in os.listdir(folder) if f.endswith('.txt')])
                    stats[split][category] = count
                else:
                    stats[split][category] = 0
        
        return stats


def main():
    """Hàm chính"""
    print("="*60)
    print("Thanh Niên Article Crawler - Crawl nội dung bài viết")
    print("="*60)
    
    # Kiểm tra database tồn tại
    if not os.path.exists(config.DB_FILE):
        print(f"\nLỗi: Database không tồn tại: {config.DB_FILE}")
        print("Vui lòng chạy collect_urls.py trước!")
        return
    
    crawler = ArticleCrawler()
    
    # Crawl
    results = crawler.crawl_all()
    
    # Hiển thị kết quả
    print("\n" + "="*60)
    print("Kết quả crawl:")
    print("="*60)
    for category, counts in results.items():
        print(f"\n{category}:")
        print(f"  Train: {counts['train']}/{config.TRAIN_SAMPLES[category]}")
        print(f"  Test: {counts['test']}/{config.TEST_SAMPLES[category]}")
    
    # Thống kê dataset
    print("\n" + "="*60)
    print("Thống kê Dataset:")
    print("="*60)
    stats = crawler.get_dataset_statistics()
    
    print("\nTrain:")
    for category, count in stats['train'].items():
        print(f"  {category}: {count} files")
    
    print("\nTest:")
    for category, count in stats['test'].items():
        print(f"  {category}: {count} files")
    
    total_train = sum(stats['train'].values())
    total_test = sum(stats['test'].values())
    print(f"\nTổng: {total_train + total_test} files (Train: {total_train}, Test: {total_test})")
    
    print("\n" + "="*60)
    print(f"Hoàn tất! Dataset: {config.OUTPUT_DIR}/")
    print("="*60)


if __name__ == "__main__":
    main()
