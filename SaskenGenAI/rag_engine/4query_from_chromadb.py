import chromadb

# 🔧 Setup ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path="chromadb")
collection = chroma_client.get_or_create_collection(name="trailer_parts")

print("🔍 Trailer Parts Search (via ChromaDB)")
print("Type your product query below (or type 'exit' to quit):\n")

# 🔁 Search loop
while True:
    user_query = input("🧠 Enter your product search query: ").strip()
    if user_query.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    # 🔎 Perform ChromaDB query
    results = collection.query(query_texts=[user_query], n_results=5)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        print("❌ No matching products found.\n")
    else:
        print(f"✅ Found {len(documents)} matching products:\n")
        for i, metadata in enumerate(metadatas, 1):
            name = metadata.get("name", "No title")
            price = metadata.get("price", "N/A")
            url = metadata.get("url", "#")
            source = metadata.get("source_site", "Unknown")
            image_url = metadata.get("image_url", "https://via.placeholder.com/150")

            print(f"🔹 {i}. {name}")
            print(f"   💰 Price: ${price}")
            print(f"   🌐 Source: {source}")
            print(f"   🔗 URL: {url}")
            print(f"   🖼️ Image: {image_url}")
            print("-" * 60)
