#!/usr/bin/env python3
"""
Complete pipeline to crawl Thanh Nien articles.
This script combines URL collection and article crawling.
"""

import argparse
from src import setup_logger, URLCollector, ArticleCrawler, DatabaseManager


def main():
    """Main pipeline function."""
    parser = argparse.ArgumentParser(
        description='Complete Thanh Nien crawler pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python thanhnien_crawler.py --collect-only      # Chỉ thu thập URLs
  python thanhnien_crawler.py --crawl-only        # Chỉ crawl articles
  python thanhnien_crawler.py                     # Chạy toàn bộ pipeline
        '''
    )
    parser.add_argument('--collect-only', action='store_true', 
                        help='Only collect URLs from RSS feeds')
    parser.add_argument('--crawl-only', action='store_true', 
                        help='Only crawl articles from database')
    parser.add_argument('--stats', action='store_true', 
                        help='Show database statistics only')
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger()
    
    # Hiển thị thống kê
    if args.stats:
        db = DatabaseManager()
        stats = db.get_stats()
        print("\n" + "="*60)
        print("Database Statistics:")
        print("="*60)
        print(f"Total articles: {stats['total']}")
        print(f"Crawled: {stats['crawled']}")
        print(f"Uncrawled: {stats['uncrawled']}")
        print(f"\nBy category:")
        for category, count in stats['by_category'].items():
            print(f"  - {category}: {count}")
        print("="*60 + "\n")
        return
    
    # Bước 1: Thu thập URLs
    if not args.crawl_only:
        logger.info("="*60)
        logger.info("STEP 1: Collecting URLs from RSS feeds")
        logger.info("="*60)
        
        collector = URLCollector()
        total_new = collector.collect_all()
        logger.info(f"Collected {total_new} new URLs\n")
    
    # Bước 2: Crawl articles
    if not args.collect_only:
        logger.info("="*60)
        logger.info("STEP 2: Crawling article content")
        logger.info("="*60)
        
        crawler = ArticleCrawler()
        stats = crawler.crawl_all()
        
        logger.info("\n" + "="*60)
        logger.info("Pipeline completed successfully!")
        logger.info(f"Train: {stats['train']}")
        logger.info(f"Test: {stats['test']}")
        logger.info("="*60 + "\n")


if __name__ == "__main__":
    main()
