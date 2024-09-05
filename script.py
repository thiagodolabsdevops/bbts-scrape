import requests
from bs4 import BeautifulSoup
import csv
import os

# URL for scraping with pagination support
base_url = "https://www.bigbadtoystore.com/Search?HideInStock=false&HidePreorder=false&HideSoldOut=false&InventoryStatus=i,p,so&PageSize=100&SortOrder=Relevance&SearchText=marvel%20legends&o={}"

def scrape_page(page_number):
    """Scrape a single page of Marvel Legends products."""
    url = base_url.format(page_number * 100)
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve page {page_number}, status code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for any product elements
    product_elements = soup.find_all("div", class_="search-result-contents")
    if not product_elements:
        print(f"No products found on page {page_number}")
        return []
    
    products = []
    for item in product_elements:
        try:
            name = item.find("span", class_="product-name").text.strip()
            company = item.find("span", class_="search-product-companies").text.strip()
            price_integer = item.find("span", class_="search-price-integer").text.strip()
            price_decimal = item.find("span", class_="search-price-decimal").text.strip()
            price = f"${price_integer}.{price_decimal}"
            status = item.find("div", class_="search-in-stock-box").text.strip() if item.find("div", class_="search-in-stock-box") else "Unavailable"
            sale_info = item.find("div", class_="search-on-sale-box").text.strip() if item.find("div", class_="search-on-sale-box") else "No sale"
            discount = item.find("span", class_="search-discount-pct").text.strip() if item.find("span", class_="search-discount-pct") else "No discount"

            products.append({
                "Name": name,
                "Company": company,
                "Price": price,
                "Status": status,
                "Sale Info": sale_info,
                "Discount": discount
            })

        except AttributeError:
            # Skip products with missing information
            continue

    return products

def scrape_all_pages(max_pages=5):
    """Scrape all pages up to the max_pages limit."""
    all_products = []
    for page_number in range(max_pages):
        print(f"Scraping page {page_number + 1}...")
        products = scrape_page(page_number)
        if not products:
            break
        all_products.extend(products)
    
    return all_products

def save_to_csv(products, filename='outputs.csv'):
    """Save the scraped product data to a CSV file."""
    keys = ["Name", "Company", "Price", "Status", "Sale Info", "Discount"]
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        if not file_exists:
            writer.writeheader()
        writer.writerows(products)

if __name__ == "__main__":
    print("Starting to scrape Marvel Legends...")
    products = scrape_all_pages()

    if not os.path.exists('outputs.csv'):
        # Ensure the file is created on the first run even if no products are found
        save_to_csv(products)
        if products:
            print(f"Scraped {len(products)} products and saved to outputs.csv")
        else:
            print("No products found. Created outputs.csv with headers.")
    else:
        if products:
            save_to_csv(products)
            print(f"Found {len(products)} new products. Updated outputs.csv.")
        else:
            print("No new products found. Skipping commit.")
            exit(0)  # Gracefully end the workflow
