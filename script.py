import requests
from bs4 import BeautifulSoup
import csv

# URL for scraping with pagination support
base_url = "https://www.bigbadtoystore.com/Search?HideInStock=false&HidePreorder=false&HideSoldOut=false&InventoryStatus=i,p,so&PageSize=100&SortOrder=Relevance&SearchText=marvel%20legends&o={}"

def scrape_page(page_number):
    """Scrape a single page of Marvel Legends products."""
    url = base_url.format(page_number * 100)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []

    for item in soup.find_all("div", class_="search-result-contents"):
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
    keys = products[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(products)

if __name__ == "__main__":
    print("Starting to scrape Marvel Legends...")
    products = scrape_all_pages()
    if products:
        save_to_csv(products)
        print(f"Scraped {len(products)} products and saved to outputs.csv")
    else:
        print("No products found.")
