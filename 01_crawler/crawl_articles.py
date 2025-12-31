#!/usr/bin/env python3
"""
Script to crawl article content from URLs in database.
"""

import argparse
from src import setup_logger, ArticleCrawler


def main():
    """Main function to crawl articles."""
    parser = argparse.ArgumentParser(description='Crawl article content from database URLs')
    parser.add_argument('--category', '-c', choices=['thoisu', 'kinhte', 'congnghe'], 
                        help='Crawl specific category only')
    parser.add_argument('--split', '-s', choices=['train', 'test'], 
                        help='Crawl specific split only')
    parser.add_argument('--count', '-n', type=int, 
                        help='Number of articles to crawl (overrides config)')
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger()
    logger.info("Starting article crawler...")
    
    # Tạo crawler
    crawler = ArticleCrawler()
    
    # Crawl dựa trên arguments
    if args.category and args.split:
        # Crawl một category và split cụ thể
        count = crawler.crawl_category(args.category, args.split, args.count)
        logger.info(f"Crawled {count} articles for {args.category} ({args.split})")
    elif args.category:
        # Crawl một category cho cả train và test
        stats = {}
        for split in ['train', 'test']:
            count = crawler.crawl_category(args.category, split, args.count)
            stats[split] = count
        logger.info(f"Crawled {args.category}: {stats}")
    else:
        # Crawl tất cả
        stats = crawler.crawl_all()
        logger.info("Crawling completed!")


if __name__ == "__main__":
    main()
