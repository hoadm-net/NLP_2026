import os
import json
import csv
import config


def create_output_dir():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)
        print(f"Created directory: {config.OUTPUT_DIR}")


def save_to_csv(articles, filepath):
    """
    Save data to CSV file.
    
    Args:
        articles: List of dictionaries containing article information
        filepath: Path to CSV file
    """
    if not articles:
        return
    
    keys = articles[0].keys()
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(articles)
    
    print(f"Saved {len(articles)} articles to {filepath}")


def save_to_json(articles, filepath):
    """
    Save data to JSON file.
    
    Args:
        articles: List of dictionaries containing article information
        filepath: Path to JSON file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(articles)} articles to {filepath}")


def clean_text(text):
    """
    Clean text by removing extra whitespace.
    
    Args:
        text: String to clean
        
    Returns:
        Cleaned string
    """
    if not text:
        return ""
    
    # Loại bỏ khoảng trắng thừa
    text = ' '.join(text.split())
    text = text.strip()
    
    return text
