"""Module for caching web scraping results to avoid redundant requests."""

import os
import json
import hashlib
from datetime import datetime, timedelta
import pickle

# Define cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

def ensure_cache_dir():
    """Ensure the cache directory exists."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def generate_cache_key(url):
    """Generate a unique cache key based on the URL."""
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def get_cache_path(cache_key):
    """Get the file path for a cache key."""
    ensure_cache_dir()
    return os.path.join(CACHE_DIR, f"{cache_key}.pickle")

def save_to_cache(url, content, metadata=None, expiry_hours=24):
    """
    Save content to cache with metadata and expiry time.
    
    Args:
        url: The URL that was scraped
        content: The content to cache
        metadata: Additional information about the cached content
        expiry_hours: Number of hours before cache expires
    """
    ensure_cache_dir()
    cache_key = generate_cache_key(url)
    cache_path = get_cache_path(cache_key)
   
    expiry_time = datetime.now() + timedelta(hours=expiry_hours)
    
    cache_data = {
        'url': url,
        'content': content,
        'metadata': metadata or {},
        'timestamp': datetime.now().isoformat(),
        'expiry': expiry_time.isoformat()
    }
    
    with open(cache_path, 'wb') as f:
        pickle.dump(cache_data, f)
    
    # Create an index file for easier browsing
    update_cache_index(url, cache_key, expiry_time)
    
    return cache_key

def load_from_cache(url):
    """
    Load content from cache if it exists and is not expired.
    
    Args:
        url: The URL to check in cache
        
    Returns:
        tuple: (content, metadata) if cache hit, (None, None) if cache miss
    """
    cache_key = generate_cache_key(url)
    cache_path = get_cache_path(cache_key)
    
    if not os.path.exists(cache_path):
        return None, None
    
    try:
        with open(cache_path, 'rb') as f:
            cache_data = pickle.load(f)
        
        # Check if cache is expired
        expiry_time = datetime.fromisoformat(cache_data['expiry'])
        if datetime.now() > expiry_time:
            # Cache expired
            return None, None
        
        return cache_data['content'], cache_data['metadata']
    
    except (json.JSONDecodeError, KeyError, ValueError):
        # Cache file is corrupt
        return None, None

def update_cache_index(url, cache_key, expiry_time):
    """Update the cache index file for easier browsing."""
    ensure_cache_dir()
    index_path = os.path.join(CACHE_DIR, "index.json")
    
    index_data = {}
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except json.JSONDecodeError:
            index_data = {}
    
    index_data[cache_key] = {
        'url': url,
        'expiry': expiry_time.isoformat(),
        'created': datetime.now().isoformat()
    }
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2)

def clean_expired_cache():
    """Remove expired cache entries."""
    ensure_cache_dir()
    index_path = os.path.join(CACHE_DIR, "index.json")
    
    if not os.path.exists(index_path):
        return
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        current_time = datetime.now()
        to_remove = []
        
        for cache_key, info in index_data.items():
            expiry_time = datetime.fromisoformat(info['expiry'])
            if current_time > expiry_time:
                cache_path = get_cache_path(cache_key)
                if os.path.exists(cache_path):
                    os.remove(cache_path)
                to_remove.append(cache_key)

        # Update the index
        for key in to_remove:
            del index_data[key]
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)
    
    except (json.JSONDecodeError, KeyError, ValueError):
        # If index is corrupt, recreate it
        if os.path.exists(index_path):
            os.remove(index_path)
