import json
import os
import glob
from datetime import datetime

# 📁 Fixed absolute path to data folder
DATA_DIR = r"C:\Users\PAVITHRA R\Desktop\GenAI\Internship\Scrapers\data"

# 🔍 Utility: get latest file matching wildcard
def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)

# ✅ Normalize eBay data
def normalize_ebay(data):
    return [{
        "name": item.get("title", "").strip(),
        "price": item.get("price", "").strip(),
        "url": item.get("link", "").strip(),
        "source_site": "eBay",
        "image_url": item.get("image_url", "https://via.placeholder.com/150")
    } for item in data if isinstance(item, dict)]

# ✅ Normalize trailerpartsunlimited data
def normalize_trailerparts(data):
    return [{
        "name": item.get("name", "").strip(),
        "price": item.get("price", "").strip(),
        "url": item.get("url", "").strip(),
        "source_site": "trailerpartsunlimited.com",
        "image_url": item.get("image_url", "https://via.placeholder.com/150")
    } for item in data if isinstance(item, dict)]

# 📂 Show all JSON files in external data folder
print("\n📂 Available files:")
for f in glob.glob(os.path.join(DATA_DIR, "*.json")):
    print(f)

# 🔄 Locate latest files
ebay_file = get_latest_file(os.path.join(DATA_DIR, "ebay_products_20*.json"))
tpu_file = get_latest_file(os.path.join(DATA_DIR, "trailerpartsunlimited_products_20*.json"))

merged_data = []
total_ebay = 0
total_tpu = 0

# 📥 Load and normalize eBay
if ebay_file:
    with open(ebay_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        norm = normalize_ebay(data)
        merged_data.extend(norm)
        total_ebay = len(norm)
        print(f"✅ Loaded {total_ebay} eBay items from {ebay_file}")
else:
    print("⚠️ No eBay file found.")

# 📥 Load and normalize trailerpartsunlimited
if tpu_file:
    with open(tpu_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        norm = normalize_trailerparts(data)
        merged_data.extend(norm)
        total_tpu = len(norm)
        print(f"✅ Loaded {total_tpu} trailerpartsunlimited items from {tpu_file}")
else:
    print("⚠️ No trailerpartsunlimited file found.")

# 💾 Save merged output in current working directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
output_path = f"merged_trailer_parts_{timestamp}.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=4, ensure_ascii=False)

# ✅ Final summary
print(f"\n📦 Merged {total_ebay} eBay + {total_tpu} trailerpartsunlimited products into '{output_path}'")
