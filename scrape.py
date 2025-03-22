"""Module for web scraping using Selenium with Bright Data proxy and BeautifulSoup."""

import os
import time
from datetime import datetime

from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Import the cache manager
from cache_manager import load_from_cache, save_to_cache, clean_expired_cache

load_dotenv()

AUTH = os.getenv('BRD_AUTH')
SBR_WEBDRIVER = f'https://{AUTH}@brd.superproxy.io:9515'

def scrape_website(website, use_cache=True, cache_expiry_hours=24):
    """Scrape website content using Selenium with Bright Data proxy, 
    handling captcha automatically. Uses cache when available and requested."""
    
    # Clean expired cache entries at the start
    clean_expired_cache()
    
    # Check cache first if enabled
    if use_cache:
        cached_content, metadata = load_from_cache(website)
        if cached_content:
            timestamp = metadata.get('timestamp', 'unknown') if metadata else 'unknown'
            print(f"Loading from cache. Cached on: {timestamp}")
            return cached_content
    
    print("Connecting to Scraping Browser...")
    start_time = time.time()
    
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, "goog", "chrome")
    with Remote(sbr_connection, options=ChromeOptions()) as driver:
        driver.get(website)
        print("Waiting captcha to solve...")
        solve_res = driver.execute(
            "executeCdpCommand",
            {
                "cmd": "Captcha.waitForSolve",
                "params": {"detectTimeout": 10000},
            },
        )
        print("Captcha solve status:", solve_res["value"]["status"])
        print("Navigated! Scraping page content...")
        html = driver.page_source
        
        # Save to cache if enabled
        if use_cache:
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'scrape_time_seconds': time.time() - start_time,
                'captcha_status': solve_res["value"]["status"]
            }
            save_to_cache(website, html, metadata, cache_expiry_hours)
            print(f"Saved to cache. Scrape time: {metadata['scrape_time_seconds']:.2f} seconds")
        
        return html


def extract_body_content(html_content):
    """Extract body content from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content):
    """Clean HTML body content by removing scripts, styles and formatting text."""
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content


def split_dom_content(dom_content, max_length=6000):
    """Split DOM content into chunks of specified maximum length."""
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]
