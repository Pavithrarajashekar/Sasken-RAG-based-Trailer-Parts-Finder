import time
import csv
import json
import logging
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Setup Folders ---
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# --- Setup Logging ---
log_file = f"logs/ebay_scrape_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- Setup Chrome Options ---
options = Options()
# options.add_argument("--headless")  # Uncomment to run headless
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0")

# --- Launch WebDriver ---
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- Search URLs ---
urls = [
    "https://www.ebay.com/sch/i.html?_nkw=trailer+axles&_sacat=0"
    
]
    

all_data = []

# --- Scrape Loop ---
for base_url in urls:
    current_url = base_url
    while True:
        logging.info(f"🌐 Scraping: {current_url}")
        driver.get(current_url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.s-item"))
            )
        except Exception as e:
            logging.warning(f"⚠️ Page load failed: {e}")
            break

        items = driver.find_elements(By.CSS_SELECTOR, "li.s-item")

        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, ".s-item__title").text.strip()
                if not title or "results matching" in title.lower():
                    continue

                price_elem = item.find_element(By.CSS_SELECTOR, ".s-item__price")
                price = price_elem.text.replace("$", "").replace(",", "").strip()

                link = item.find_element(By.CSS_SELECTOR, ".s-item__link").get_attribute("href")

                # --- Extract Image from Product Page ---
                image_url = "https://via.placeholder.com/150"
                try:
                    original_window = driver.current_window_handle
                    driver.execute_script("window.open('');")
                    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(link)

                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.ux-image-carousel-item img"))
                    )

                    img_el = driver.find_element(By.CSS_SELECTOR, "div.ux-image-carousel-item img")
                    src = img_el.get_attribute("src")
                    if src and not src.endswith("1x1.gif"):
                        image_url = src

                    driver.close()
                    driver.switch_to.window(original_window)
                except Exception as e:
                    logging.warning(f"⚠️ Could not get image for '{title}': {e}")
                    try:
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(original_window)
                    except:
                        pass

                product = {
                    "title": title,
                    "price": price,
                    "link": link,
                    "seller": "eBay",
                    "source": base_url,
                    "timestamp": datetime.now().isoformat(),
                    "image_url": image_url
                }
                all_data.append(product)

            except Exception as e:
                logging.debug(f"🔁 Skipped item due to error: {e}")
                continue

        # --- Handle Pagination ---
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a.pagination__next")
            if "pagination__next--disabled" in next_btn.get_attribute("class"):
                break
            current_url = next_btn.get_attribute("href")
            time.sleep(1)
        except:
            break

driver.quit()

# --- Save Output Files ---
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
json_file = f"data/ebay_products_{timestamp}.json"
csv_file = f"data/ebay_products_{timestamp}.csv"

with open(json_file, "w", encoding="utf-8") as f_json:
    json.dump(all_data, f_json, indent=2, ensure_ascii=False)

csv_fields = list(all_data[0].keys()) if all_data else [
    "title", "price", "link", "seller", "source", "timestamp", "image_url"
]
with open(csv_file, "w", newline="", encoding="utf-8") as f_csv:
    writer = csv.DictWriter(f_csv, fieldnames=csv_fields)
    writer.writeheader()
    writer.writerows(all_data)

logging.info(f"✅ Scraped {len(all_data)} items.")
print(f"✅ Done! Scraped {len(all_data)} products from eBay.")
print(f"📝 Saved to {json_file} and {csv_file}")

