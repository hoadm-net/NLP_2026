#!/usr/bin/env python3
"""
Script to collect article URLs from RSS feeds and save to database.
"""

import argparse
from src import setup_logger, URLCollector, DatabaseManager


def main():
    """Main function to collect URLs from RSS feeds."""
    parser = argparse.ArgumentParser(description='Collect article URLs from RSS feeds')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger()
    logger.info("Starting URL collection from RSS feeds...")
    
    # Tạo collector và thu thập URLs
    collector = URLCollector()
    total_new = collector.collect_all()
    
    # Hiển thị thống kê
    db = DatabaseManager()
    stats = db.get_stats()
    
    print("\n" + "="*60)
    print("Database Statistics:")
    print("="*60)
    print(f"Total articles: {stats['total']}")
    print(f"\nBy category:")
    for category, count in stats['by_category'].items():
        print(f"  - {category}: {count}")
    print(f"\nCrawled: {stats['crawled']}")
    print(f"Uncrawled: {stats['uncrawled']}")
    print("="*60)
    
    logger.info(f"Collection completed! {total_new} new URLs added to database.")


if __name__ == "__main__":
    main()

    
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
