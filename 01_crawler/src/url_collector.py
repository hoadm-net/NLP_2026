import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import logging
from tqdm import tqdm

import config
from .database import DatabaseManager


class URLCollector:
    """Collector for URLs from RSS feeds."""
    
    def __init__(self):
        """Initialize URL collector."""
        self.logger = logging.getLogger('ThanhNienCrawler')
        self.db = DatabaseManager()
        
    def parse_rss(self, rss_url, category):
        """
        Parse RSS feed and extract article information.
        
        Args:
            rss_url: URL of RSS feed
            category: Category name (thoisu, kinhte, congnghe)
            
        Returns:
            List of dictionaries containing article information
        """
        try:
            response = requests.get(rss_url, headers=config.HEADERS, timeout=config.TIMEOUT)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            articles = []
            
            # Tìm tất cả items trong channel
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
            
            self.logger.info(f"Parsed {len(articles)} articles from {category}")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error parsing RSS feed {rss_url}: {e}")
            return []
    
    def save_to_database(self, articles):
        """
        Save articles to database.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Number of new articles saved
        """
        new_count = 0
        
        for article in articles:
            if self.db.insert_article(article):
                new_count += 1
        
        return new_count
    
    def collect_from_rss(self, category, rss_url):
        """
        Collect URLs from a single RSS feed.
        
        Args:
            category: Category name
            rss_url: URL of RSS feed
            
        Returns:
            Number of new articles collected
        """
        self.logger.info(f"Collecting URLs from {category} RSS feed...")
        
        articles = self.parse_rss(rss_url, category)
        
        if articles:
            new_count = self.save_to_database(articles)
            self.logger.info(f"Saved {new_count} new articles from {category}")
            return new_count
        
        return 0
    
    def collect_all(self):
        """
        Collect URLs from all RSS feeds defined in config.
        
        Returns:
            Total number of new articles collected
        """
        total_new = 0
        
        for category, rss_url in tqdm(config.RSS_FEEDS.items(), desc="Collecting URLs"):
            new_count = self.collect_from_rss(category, rss_url)
            total_new += new_count
            time.sleep(config.DELAY_BETWEEN_REQUESTS)
        
        # In thống kê
        stats = self.db.get_stats()
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"Collection Summary:")
        self.logger.info(f"  Total articles in database: {stats['total']}")
        self.logger.info(f"  New articles collected: {total_new}")
        self.logger.info(f"  By category: {stats['by_category']}")
        self.logger.info(f"{'='*50}\n")
        
        return total_new
