import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_website(url):
    try:
        driver = get_driver()
    except Exception as e:
        print(f"Driver Error: {e}")
        raise Exception(f"Failed to start Chrome. Make sure Google Chrome is installed on your system. Error: {str(e)}")
    
    try:
        driver.get(url)
        time.sleep(3)
        html = driver.page_source
        
        # Take screenshot for vision
        screenshot_path = "page.png"
        driver.save_screenshot(screenshot_path)
        
        return html, screenshot_path
    finally:
        driver.quit()

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    cleaned_content = soup.get_text(separator=" ")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    return cleaned_content
