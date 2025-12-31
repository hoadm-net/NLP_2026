import requests
from bs4 import BeautifulSoup
import os
import time
import logging
from tqdm import tqdm
import random

import config
from .database import DatabaseManager
from .file_utils import clean_text


class ArticleCrawler:
    """Crawler for article content from URLs in database."""
    
    def __init__(self):
        """Initialize article crawler."""
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.logger = logging.getLogger('ThanhNienCrawler')
        self.db = DatabaseManager()
        self.setup_folders()
        
    def setup_folders(self):
        """Create directory structure for storing articles."""
        base_dir = config.OUTPUT_DIR
        
        # Train folders
        for category in config.TRAIN_SAMPLES.keys():
            train_path = os.path.join(base_dir, config.TRAIN_DIR, category)
            os.makedirs(train_path, exist_ok=True)
        
        # Test folders
        for category in config.TEST_SAMPLES.keys():
            test_path = os.path.join(base_dir, config.TEST_DIR, category)
            os.makedirs(test_path, exist_ok=True)
        
        self.logger.info(f"Created folder structure at: {base_dir}")
    
    def get_page(self, url, retries=config.MAX_RETRIES):
        """
        Get page content from URL.
        
        Args:
            url: URL to fetch
            retries: Number of retry attempts
            
        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=config.TIMEOUT)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'lxml')
            except requests.RequestException as e:
                self.logger.warning(f"Error accessing {url} (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(config.DELAY_BETWEEN_REQUESTS)
                else:
                    self.logger.error(f"Failed to access {url} after {retries} attempts")
                    return None
    
    def extract_article_content(self, url):
        """
        Extract article content from URL.
        
        Args:
            url: Article URL
            
        Returns:
            String containing article content or None if failed
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
                self.logger.warning(f"No content found for {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def save_article(self, content, category, split, index):
        """
        Save article content to file.
        
        Args:
            content: Article content string
            category: Category name (thoisu, kinhte, congnghe)
            split: train or test
            index: Index number for filename
            
        Returns:
            Path to saved file or None if failed
        """
        if not content:
            return None
        
        filename = f"{category}_{index:04d}.txt"
        filepath = os.path.join(config.OUTPUT_DIR, split, category, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return filepath
        except Exception as e:
            self.logger.error(f"Error saving file {filepath}: {e}")
            return None
    
    def crawl_category(self, category, split='train', target_count=None):
        """
        Crawl articles for a specific category and split.
        
        Args:
            category: Category name (thoisu, kinhte, congnghe)
            split: train or test
            target_count: Number of articles to crawl
            
        Returns:
            Number of articles successfully crawled
        """
        if target_count is None:
            target_count = config.TRAIN_SAMPLES.get(category, 0) if split == 'train' else config.TEST_SAMPLES.get(category, 0)
        
        self.logger.info(f"Crawling {target_count} articles for {category} ({split})")
        
        # Lấy URLs chưa crawl từ database
        urls = self.db.get_uncrawled_urls(category=category, limit=target_count * 2)  # Lấy dư để đề phòng
        
        if not urls:
            self.logger.warning(f"No URLs available for {category}")
            return 0
        
        success_count = 0
        
        for article_id, url, _ in tqdm(urls, desc=f"{category} ({split})"):
            if success_count >= target_count:
                break
            
            # Crawl content
            content = self.extract_article_content(url)
            
            if content:
                # Lưu vào file
                filepath = self.save_article(content, category, split, success_count + 1)
                if filepath:
                    success_count += 1
                    self.db.mark_as_crawled(article_id)
                    self.db.mark_as_used(article_id)
            else:
                # Đánh dấu là đã crawl nhưng không dùng
                self.db.mark_as_crawled(article_id)
            
            # Delay giữa các request
            time.sleep(config.DELAY_BETWEEN_REQUESTS + random.uniform(0, 0.5))
        
        self.logger.info(f"Successfully crawled {success_count}/{target_count} articles for {category} ({split})")
        return success_count
    
    def crawl_all(self):
        """
        Crawl all articles for all categories (train and test).
        
        Returns:
            Dictionary with statistics
        """
        stats = {'train': {}, 'test': {}}
        
        # Crawl train data
        self.logger.info("\n" + "="*50)
        self.logger.info("Crawling TRAIN data")
        self.logger.info("="*50)
        
        for category in config.TRAIN_SAMPLES.keys():
            count = self.crawl_category(category, 'train')
            stats['train'][category] = count
        
        # Crawl test data
        self.logger.info("\n" + "="*50)
        self.logger.info("Crawling TEST data")
        self.logger.info("="*50)
        
        for category in config.TEST_SAMPLES.keys():
            count = self.crawl_category(category, 'test')
            stats['test'][category] = count
        
        # In summary
        self.logger.info("\n" + "="*50)
        self.logger.info("Crawling Summary:")
        self.logger.info(f"  Train: {stats['train']}")
        self.logger.info(f"  Test: {stats['test']}")
        self.logger.info("="*50 + "\n")
        
        return stats
