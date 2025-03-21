from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import time

def scrape_website(url):
    """Scrape un site web en utilisant Selenium avec Chromium."""
    print(f"Configuration pour scraper {url}")
    
    # Structure de dossier pour les données du navigateur
    user_data_dir = os.path.abspath("./chrome_data")
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Chemin du chromedriver
    chrome_driver_path = os.path.abspath("./chromedriver/chromedriver")
    
    # Vérifier et configurer les permissions
    if os.path.exists(chrome_driver_path):
        os.chmod(chrome_driver_path, 0o755)
    else:
        print(f"ATTENTION: chromedriver non trouvé à {chrome_driver_path}")
    
    # Configuration des options
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium-browser"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--remote-debugging-port=9222")
    
    # Créer le service
    service = Service(chrome_driver_path)
    
    try:
        print("Lancement du navigateur...")
        driver = webdriver.Chrome(service=service, options=options)
        
        print(f"Navigation vers {url}")
        driver.get(url)
        time.sleep(5)
        
        print("Extraction du HTML...")
        html = driver.page_source
        return html
        
    except Exception as e:
        msg = f"Erreur: {str(e)}"
        print(msg)
        return msg
        
    finally:
        try:
            driver.quit()
            print("Navigateur fermé")
        except:
            pass