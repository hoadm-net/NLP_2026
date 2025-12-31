import sqlite3
import logging
import config


class DatabaseManager:
    """Manager for SQLite database operations."""
    
    def __init__(self, db_file=None):
        """
        Initialize database manager.
        
        Args:
            db_file: Path to SQLite database file
        """
        self.db_file = db_file or config.DB_FILE
        self.logger = logging.getLogger('ThanhNienCrawler')
        self.setup_database()
    
    def setup_database(self):
        """Create database and tables if they don't exist."""
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
        self.logger.info(f"Database ready: {self.db_file}")
    
    def insert_article(self, article):
        """
        Insert article into database.
        
        Args:
            article: Dictionary containing article information
            
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
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
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # URL đã tồn tại
            return False
        finally:
            conn.close()
    
    def get_uncrawled_urls(self, category=None, limit=None):
        """
        Get URLs that haven't been crawled yet.
        
        Args:
            category: Filter by category (optional)
            limit: Maximum number of URLs to return (optional)
            
        Returns:
            List of tuples (id, url, category)
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = 'SELECT id, url, category FROM articles WHERE crawled = 0'
        params = []
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def mark_as_crawled(self, article_id):
        """
        Mark article as crawled.
        
        Args:
            article_id: ID of the article in database
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('UPDATE articles SET crawled = 1 WHERE id = ?', (article_id,))
        conn.commit()
        conn.close()
    
    def mark_as_used(self, article_id):
        """
        Mark article as used in dataset.
        
        Args:
            article_id: ID of the article in database
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('UPDATE articles SET used_in_dataset = 1 WHERE id = ?', (article_id,))
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        stats = {}
        
        # Tổng số bài viết
        cursor.execute('SELECT COUNT(*) FROM articles')
        stats['total'] = cursor.fetchone()[0]
        
        # Số bài đã crawl
        cursor.execute('SELECT COUNT(*) FROM articles WHERE crawled = 1')
        stats['crawled'] = cursor.fetchone()[0]
        
        # Số bài chưa crawl
        cursor.execute('SELECT COUNT(*) FROM articles WHERE crawled = 0')
        stats['uncrawled'] = cursor.fetchone()[0]
        
        # Theo từng category
        cursor.execute('SELECT category, COUNT(*) FROM articles GROUP BY category')
        stats['by_category'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
