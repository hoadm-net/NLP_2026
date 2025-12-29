"""
Thanh Niên Crawler - Tool cào dữ liệu từ Thanh Niên (thanhnien.vn)
Bài toán: Phân loại văn bản (Topic Classification)
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import logging
import os
from datetime import datetime
from urllib.parse import urljoin
from tqdm import tqdm
import pandas as pd

import config
from utils import setup_logger, save_to_csv, save_to_json, create_output_dir


class ThanhNienCrawler:
    """Crawler chính cho Thanh Niên (thanhnien.vn)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.logger = setup_logger()
        self.articles = []
        create_output_dir()
        
    def get_page(self, url, retries=config.MAX_RETRIES):
        """
        Lấy nội dung trang web
        
        Args:
            url: URL cần crawl
            retries: Số lần thử lại
            
        Returns:
            BeautifulSoup object hoặc None nếu thất bại
        """
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
    
    def extract_article_links(self, soup, category_url):
        """
        Trích xuất các link bài viết từ trang danh mục
        
        Args:
            soup: BeautifulSoup object của trang danh mục
            category_url: URL của danh mục
            
        Returns:
            List các URL bài viết
        """
        links = []
        
        # Thanh Niên sử dụng thẻ <article> hoặc <div class="story">
        # Tìm các thẻ chứa bài viết
        article_items = soup.find_all('article', class_='story')
        
        for item in article_items:
            link_tag = item.find('a', href=True)
            if link_tag:
                article_url = link_tag['href']
                if not article_url.startswith('http'):
                    article_url = urljoin(config.BASE_URL, article_url)
                # Chỉ lấy các link bài viết, bỏ qua video, gallery
                if '.htm' in article_url and 'video' not in article_url:
                    links.append(article_url)
        
        # Thử cấu trúc khác: div.box-category-item
        if not links:
            items = soup.find_all('div', class_='box-category-item')
            for item in items:
                link_tag = item.find('a', class_='story__title', href=True)
                if link_tag:
                    article_url = link_tag['href']
                    if not article_url.startswith('http'):
                        article_url = urljoin(config.BASE_URL, article_url)
                    if '.htm' in article_url:
                        links.append(article_url)
        
        # Loại bỏ duplicate
        links = list(dict.fromkeys(links))
        
        self.logger.info(f"Tìm thấy {len(links)} bài viết trong trang")
        return links
    
    def extract_article_data(self, url):
        """
        Trích xuất dữ liệu từ một bài viết
        
        Args:
            url: URL của bài viết
            
        Returns:
            Dictionary chứa thông tin bài viết
        """
        soup = self.get_page(url)
        if not soup:details__headline')
            if not title_tag:
                title_tag = soup.find('h1', class_='article-title')
            article_data['title'] = title_tag.get_text(strip=True) if title_tag else ''
            
            # Mô tả/Sapo
            description_tag = soup.find('h2', class_='details__summary')
            if not description_tag:
                description_tag = soup.find('div', class_='sapo')
            article_data['description'] = description_tag.get_text(strip=True) if description_tag else ''
            
            # Nội dung
            content_div = soup.find('div', id='main-detail-content')
            if not content_div:
                content_div = soup.find('div', class_='details__content')
            
            if content_div:
                paragraphs = content_div.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                article_data['content'] = content
            else:
                article_data['content'] = ''
            
            # Thời gian đăng
            date_tag = soup.find('div', class_='details__meta')
            if date_tag:
                time_tag = date_tag.find('time')
                article_data['published_date'] = time_tag.get_text(strip=True) if time_tag else ''
            else:
                article_data['published_date'] = ''
            
            # Tác giả
            author_tag = soup.find('div', class_='details__author')
            article_data['author'] = author_tag.get_text(strip=True) if author_tag else ''
            
            # Danh mục (Topic Classification)
            # Xác định danh mục dựa trên URL
            if 'kinh-te' in url:
                article_data['category'] = 'kinh-te'
            elif 'cong-nghe' in url:
                article_data['category'] = 'cong-nghe'
            else:
                article_data['category'] = 'thoi-su'
            
            # Tags
            tags = []
            tag_section = soup.find('div', class_='details__
            category_tag = soup.find('ul', class_='breadcrumb')
            if category_tag:
                categories = [li.get_text(strip=True) for li in category_tag.find_all('li')]
                article_data['category'] = ' > '.join(categories)
            else:
                article_data['category'] = ''
            
            # Tags
            tags = []
            tag_section = soup.find('div', class_='tags')
            if tag_section:
                tag_links = tag_section.find_all('a')
                tags = [tag.get_text(strip=True) for tag in tag_links]
            article_data['tags'] = ', '.join(tags)
            
            self.logger.info(f"Đã crawl: {article_data['title'][:50]}...")
            return article_data
            
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất dữ liệu từ {url}: {e}")
            return None
    
    def crawl_category(self, category_name, max_articles=10):
        """
        Crawl các bài viết từ một danh mục
        
        Args:
            category_name: Tên danh mục (key trong CATEGORIES)
            max_articles: Số lượng bài viết tối đa cần crawl
        """
        if category_name not in config.CATEGORIES:
            self.logger.error(f"Danh mục '{category_name}' không tồn tại")
            return
        
        category_url = config.CATEGORIES[category_name]
        self.logger.info(f"Bắt đầu crawl danh mục: {category_name}")
        
        # Lấy trang danh mục
        soup = self.get_page(category_url)
        if not soup:
            return
        
        # Lấy danh sách link bài viết
        article_links = self.extract_article_links(soup, category_url)
        article_links = article_links[:max_articles]
        
        # Crawl từng bài viết
        for link in tqdm(article_links, desc=f"Crawling {category_name}"):
            article_data = self.extract_article_data(link)
            if article_data:
                self.articles.append(article_data)
            time.sleep(config.DELAY_BETWEEN_REQUESTS)
    
    def crawl_multiple_categories(self, categories, max_articles_per_category=10):
        """
        Crawl nhiều danh mục
        
        Args:
            categories: List các tên danh mục
            max_articles_per_category: Số bài viết tối đa mỗi danh mục
        """
        for category in categories:
            self.crawl_category(category, max_articles_per_category)
            self.logger.info(f"Đã hoàn thành crawl danh mục: {category}")
    
    def save_data(self, format='csv'):
        """
        Lưu dữ liệu đã crawl
        
        Args:
            format: Định dạng file ('csv', 'json', hoặc 'both')
        """
        if not self.articles:
            self.logger.warning("Không có dữ liệu để lưu")
            return
        
        if format in ['csv', 'both']:
            save_to_csv(self.articles, os.path.join(config.OUTPUT_DIR, config.CSV_FILE))
            self.logger.info(f"Đã lưu {len(self.articles)} bài viết vào file CSV")
        
        if forThanhNienCrawler()
    
    print("=" * 60)
    print("Thanh Niên Crawler - Topic Classification")
    print("=" * 60)
    print("\nDanh mục có sẵn:")
    for i, category in enumerate(config.CATEGORIES.keys(), 1):
        print(f"{i}. {category}")
    
    print("\nVí dụ sử dụng:")
    print("# Crawl một danh mục")
    print("crawler.crawl_category('thoi-su', max_articles=5)")
    print("\n# Crawl nhiều danh mục")
    print("crawler.crawl_multiple_categories(['thoi-su', 'kinh-tef 'content' in df.columns else 0
        }
        return stats


def main():
    """Hàm chính để chạy crawler"""
    crawler = VnExpressCrawler()
    
    print("=" * 60)
    print("VnExpress Crawler")
    print("=" * 60)
    print("\nDanh mục có sẵn:")
    for i, category in enumerate(config.CATEGORIES.keys(), 1):
        print(f"{i}. {category}")
    
    print("\nVí dụ sử dụng:")
    print("# Crawl một danh mục")
    print("crawler.crawl_category('thoi-su', max_articles=5)")
    print("\n# Crawl nhiều danh mục")
    print("crawler.crawl_multiple_categories(['thoi-su', 'the-gioi'], max_articles_per_category=5)")
    print("\n# Lưu dữ liệu")
    print("crawler.save_data(format='both')")
    
    # Demo: Crawl 5 bài viết từ danh mục "thoi-su"
    print("\n" + "=" * 60)
    print("Demo: Crawl 5 bài viết từ danh mục 'thoi-su'")
    print("=" * 60)
    crawler.crawl_category('thoi-su', max_articles=5)
    crawler.save_data(format='both')
    
    # Hiển thị thống kê
    stats = crawler.get_statistics()
    print("\nThống kê:")
    print(f"Tổng số bài viết: {stats['total_articles']}")


if __name__ == "__main__":
    main()
