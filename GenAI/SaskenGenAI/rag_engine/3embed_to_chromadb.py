import json
from sentence_transformers import SentenceTransformer
import chromadb
import os

# 💾 Connect to ChromaDB and delete existing collection
client = chromadb.PersistentClient(path="chromadb")
client.delete_collection(name="trailer_parts")
print("✅ Deleted existing 'trailer_parts' collection.")

# 📦 Load merged product chunks
chunk_file = "data/product_chunks.json"  # Update if you're using a different filename
if not os.path.exists(chunk_file):
    print(f"❌ File not found: {chunk_file}")
    exit()

with open(chunk_file, "r", encoding="utf-8") as f:
    product_chunks = json.load(f)

# 🧠 Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 🧠 Prepare embeddings
ids = [f"chunk_{i}" for i in range(len(product_chunks))]
documents = [item.get("name", "") for item in product_chunks]

# ✅ Improved metadata handling with correct source site
metadatas = []
for item in product_chunks:
    url = item.get("url", item.get("link", ""))
    
    # Infer source_site if missing
    source = item.get("source_site", "").strip()
    if not source:
        if "trailerpartsunlimited" in url:
            source = "trailerpartsunlimited.com"
        elif "ebay.com" in url:
            source = "eBay"
        else:
            source = "Unknown"

    metadatas.append({
        "name": item.get("name", ""),
        "price": item.get("price", ""),
        "url": url,
        "source_site": source,
        "image_url": item.get("image_url", "https://via.placeholder.com/150")
    })

# 🔢 Encode product names
embeddings = model.encode(documents).tolist()

# 🚀 Insert into ChromaDB
chroma_client = chromadb.PersistentClient(path="chromadb")
collection = chroma_client.get_or_create_collection(name="trailer_parts")
collection.add(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)

print(f"✅ Inserted {len(product_chunks)} products with image URLs into ChromaDB.")
