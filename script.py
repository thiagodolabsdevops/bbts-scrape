from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import csv
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

chrome_driver_path = '/opt/homebrew/bin/chromedriver' # Path to ChromeDriver executable on MacOS

# Configure WebDriver
service = ChromeService(executable_path=chrome_driver_path)
options = webdriver.ChromeOptions()
# options.add_argument('--headless') # Uncomment for headless mode
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
driver = webdriver.Chrome(service=service, options=options)

def create_url(page_index, search_text, page_size):
    return f"https://www.bigbadtoystore.com/Search?PageIndex={page_index}&PageSize={page_size}&SearchText={search_text}"

def fetch_page_document(page_index, search_text, page_size):
    url = create_url(page_index, search_text, page_size)
    logging.info(f"[PAGE {page_index}]: Fetching {url}")
    driver.get(url)
    
    try:
        logging.info(f"Waiting for page {page_index} to load...")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.results-list .row'))
        )
        logging.info(f"Page {page_index} loaded successfully.")
    except TimeoutException:
        logging.error(f"[PAGE {page_index}]: Timeout waiting for elements")
        return None

    return BeautifulSoup(driver.page_source, 'html.parser')

def get_results(soup):
    if soup is None:
        logging.error("No soup object to process.")
        return []
    
    rows = soup.select(".results-list > .row")
    if not rows:
        logging.error("No rows found in the soup object.")
        return []

    results = []
    for row in rows:
        item = {
            'name': row.select_one('.product-name').get_text(strip=True) if row.select_one('.product-name') else 'No product name',
            "status": row.select_one('.search-listing-box').get_text(strip=True) if row.select_one('.search-listing-box') else 'No status',
            "company": row.select_one('.search-product-companies').get_text(strip=True) if row.select_one('.search-product-companies') else 'No company',
            "photo": row.select_one('.search-product-thumbnail')['src'] if row.select_one('.search-product-thumbnail') else 'No photo',
        }
        results.append(item)
    
    return results

def write_to_csv(results):
    with open('outputs.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["name", "status", "company", "photo"])
        writer.writeheader()
        writer.writerows(results)

def main():
    search_text = sys.argv[1]
    page_limit = int(os.getenv('PAGE_LIMIT', 1))
    page_size = int(os.getenv('PAGE_SIZE', 100))
    has_debug = os.getenv('DEBUG') == "1"

    aggregated_results = []
    for current_page_index in range(1, page_limit + 1):
        soup = fetch_page_document(current_page_index, search_text, page_size)
        if soup is None:
            logging.error(f"[PAGE {current_page_index}]: Failed to fetch page document.")
            break

        results = get_results(soup)
        if not results:
            logging.error(f"[PAGE {current_page_index}]: No results found.")
            break

        if has_debug:
            print(f"[PAGE {current_page_index}]: Got {len(results)} results.")

        aggregated_results.extend(results)

    write_to_csv(aggregated_results)
    print("Scraping completed and results saved to outputs.csv.")

if __name__ == "__main__":
    main()
    driver.quit()
