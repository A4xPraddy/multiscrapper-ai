import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_driver():
    """Dynamically installs and configures the correct Chrome driver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # This magic line handles all version mismatch issues automatically
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_website(url):
    """Scrapes a website and returns HTML + saves a screenshot."""
    print(f"Scraping: {url}...")
    driver = get_driver()
    try:
        driver.get(url)
        time.sleep(3)  # Wait for JS to load
        
        # Take screenshot for Gemini Vision
        driver.save_screenshot("page_screenshot.png")
        
        html = driver.page_source
        return html
    finally:
        driver.quit()

def clean_body_content(html_content):
    """Extracts and cleans text from the <body> of HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove junk
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.extract()

    # Get cleaned text
    text = soup.get_text(separator=" ")
    cleaned_text = "\n".join(
        line.strip() for line in text.splitlines() if line.strip()
    )
    return cleaned_text

def split_text(text, chunk_size=2000):
    """Simple splitter for non-RAG tasks."""
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
