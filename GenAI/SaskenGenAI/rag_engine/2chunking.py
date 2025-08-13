import json
import os
import glob

# 💾 Ensure output directory exists
os.makedirs("data", exist_ok=True)

# 🔍 Automatically get the latest merged_trailer_parts_*.json file
merged_files = glob.glob("merged_trailer_parts_*.json")
if not merged_files:
    print("❌ No merged_trailer_parts_*.json file found.")
    exit()

latest_file = max(merged_files, key=os.path.getmtime)
print(f"📂 Using latest merged file: {latest_file}")

# 📂 Load merged product data
with open(latest_file, "r", encoding="utf-8") as f:
    products = json.load(f)

# 🧩 Create structured chunks
chunks = []
for item in products:
    chunk_text = f"""Product: {item.get('name', '')}
Price: {item.get('price', '')}
Source: {item.get('source_site', '')}
Link: {item.get('url', '')}"""

    chunks.append({
        "text": chunk_text.strip(),
        "name": item.get("name", ""),
        "price": item.get("price", "N/A"),
        "seller": item.get("source_site", "Unknown"),
        "link": item.get("url", "#"),
        "image_url": item.get("image_url", "https://via.placeholder.com/150")
    })

# 💾 Save the chunked data
output_file = "data/product_chunks.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=4)

print(f"✅ Saved {len(chunks)} structured product chunks to '{output_file}'")
