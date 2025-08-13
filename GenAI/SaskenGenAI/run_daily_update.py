import os
from datetime import datetime

print("🚀 Starting Daily Update Pipeline")

# 📅 Timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Step 1: Run Scrapers
print("🔍 Running scrapers...")
os.system("python Scrapers/scrape_ebay.py")
os.system("python Scrapers/scrape_trailerpartsunlimited.py")

# Step 2: Merge & Normalize
print("🔗 Merging & normalizing data...")
merge_exit = os.system("python rag_engine/1merge_and_normalize.py")
if merge_exit != 0:
    print("❌ Merge step failed. Aborting pipeline.")
    exit(1)

# Step 3: Chunk Data
print("🔪 Chunking merged data...")
chunk_exit = os.system("python rag_engine/2chunking.py")
if chunk_exit != 0:
    print("❌ Chunking step failed. Aborting pipeline.")
    exit(1)

# Step 4: Embed into ChromaDB
print("🧠 Embedding to ChromaDB...")
embed_exit = os.system("python rag_engine/3embed_to_chromadb.py")
if embed_exit != 0:
    print("❌ Embedding step failed.")
    exit(1)

# ✅ Final Status
print(f"\n✅ Daily update completed successfully at {timestamp}")
