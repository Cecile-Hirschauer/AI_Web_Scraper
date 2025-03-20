import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
import time

def scrape_website(url):
    print("Launching Chrome browser...")

    chrome_driver_path = "/usr/local/bin/chromedriver"
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    try:
        driver.get(url)
        print(f"Page loaded ...")
        html = driver.page_source
        time.sleep(10)
        return html
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()