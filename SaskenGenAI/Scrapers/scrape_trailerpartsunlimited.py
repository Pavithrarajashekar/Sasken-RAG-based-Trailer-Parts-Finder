import time
import json
import csv
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import re

# --- Setup ---
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)
log_file = f"logs/trailerpartsunlimited_scrape_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("🚚 Starting scrape_trailerpartsunlimited script")

# --- Selenium config ---
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- Target URLs ---
urls = [
    "https://trailerpartsunlimited.com/single-axle-trailer-kits-with-electric-brakes/",
    "https://trailerpartsunlimited.com/single-axle-kits/",
    "https://trailerpartsunlimited.com/categories/axles/single-axle-kits/3-5k-single-axle-kits.html",
    "https://trailerpartsunlimited.com/categories/axles/single-axle-kits/5-2k-single-axle-kits.html",
    "https://trailerpartsunlimited.com/categories/axles/7k-single-axle-kits.html",
    "https://trailerpartsunlimited.com/categories/axles/single-axle-kits/6k-single-axle-kits.html"
]

all_products = []

for url in urls:
    logging.info(f"🌐 Scraping URL: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".productGrid .card"))
        )
        products = driver.find_elements(By.CSS_SELECTOR, ".productGrid .card")
        logging.info(f"✅ Found {len(products)} products on {url}.")
    except Exception as e:
        logging.error(f"❌ Could not load product list: {e}")
        continue

    for p in products:
        try:
            # --- Name & URL ---
            name = ""
            product_url = ""
            for sel in ["h4.card-title a", ".card-title a", ".card-title", ".name a"]:
                try:
                    elem = p.find_element(By.CSS_SELECTOR, sel)
                    name = elem.text.strip()
                    product_url = elem.get_attribute("href") or url
                    break
                except:
                    continue

            if not name:
                logging.warning("⚠️ Skipped product — no name found.")
                continue

            # --- Price ---
            price = "N/A"
            try:
                price_block = p.find_element(By.CSS_SELECTOR, ".card-body .price--withoutTax, .card-body .price--main, .card-body .price")
                price_text = price_block.text.strip()
                prices_found = re.findall(r"\$?\d{1,4}\.\d{2}", price_text)
                if prices_found:
                    price = prices_found[-1].replace("$", "")
                else:
                    # Fallback: search all card-body text
                    fallback_text = p.find_element(By.CSS_SELECTOR, ".card-body").text.strip()
                    prices_found = re.findall(r"\$?\d{1,4}\.\d{2}", fallback_text)
                    if prices_found:
                        price = prices_found[-1].replace("$", "")
            except Exception as e:
                logging.debug(f"Price not found: {e}")

            # --- Image URL ---
            try:
                img_el = p.find_element(By.CSS_SELECTOR, "img")
                image_url = img_el.get_attribute("data-src") or img_el.get_attribute("src") or ""
                if "placeholder" in image_url or not image_url:
                    image_url = "https://via.placeholder.com/150"
            except:
                image_url = "https://via.placeholder.com/150"

            # --- Append Product ---
            product_info = {
                "name": name,
                "price": price,
                "url": product_url,
                "source_site": "trailerpartsunlimited.com",
                "image_url": image_url
            }
            all_products.append(product_info)

        except Exception as e:
            logging.warning(f"⚠️ Skipped a product due to error: {e}")
            continue

driver.quit()

# --- Save CSV ---
timestamp = datetime.now().strftime("%Y%m%d")
csv_file = f"data/trailerpartsunlimited_products_{timestamp}.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "price", "url", "source_site", "image_url"])
    writer.writeheader()
    writer.writerows(all_products)

# --- Save JSON ---
timestamp_json = datetime.now().strftime("%Y%m%d_%H%M")
relative_path = f"data/trailerpartsunlimited_products_{timestamp_json}.json"
abs_path = os.path.abspath(relative_path)

with open(abs_path, "w", encoding="utf-8") as f_json:
    json.dump(all_products, f_json, indent=4, ensure_ascii=False)

message = f"✅ Saved {len(all_products)} products to {relative_path}"
logging.info(message)
print(message)
