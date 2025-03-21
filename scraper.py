from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv

load_dotenv()

AUTH = os.getenv('BRD_AUTH')
SBR_WEBDRIVER = f'https://{AUTH}@brd.superproxy.io:9515'


def scrape_website(url):
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
    with Remote(sbr_connection, options=ChromeOptions()) as driver:
        print('Connected! Navigating...')
        driver.get('https://amazon.fr')
        print('Taking page screenshot to file page.png')
        driver.get_screenshot_as_file('./page.png')
        print('Navigated! Scraping page content...')
        html = driver.page_source
        return html
