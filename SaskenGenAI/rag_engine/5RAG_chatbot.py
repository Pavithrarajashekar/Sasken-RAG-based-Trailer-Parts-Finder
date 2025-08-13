import chromadb
import requests

# 🔗 Ollama settings
OLLAMA_MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434/api/generate"

# 🔍 Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path="chromadb")
collection = chroma_client.get_or_create_collection(name="trailer_parts")

# 🧠 Helper to format product context
def format_context(metadatas):
    chunks = []
    for meta in metadatas:
        name = meta.get("name", "No Name")
        price = meta.get("price", "N/A")
        source = meta.get("source_site", "Unknown")
        url = meta.get("url", "#")
        chunks.append(f"- {name}\n  Price: ${price}\n  Source: {source}\n  Link: {url}")
    return "\n\n".join(chunks)

# 💬 Query loop
print("🤖 RAG Chatbot (LLaMA 3 + ChromaDB)")
print("Type your query below (or 'exit' to quit):\n")

while True:
    user_query = input("🧠 You: ").strip()
    if user_query.lower() in ("exit", "quit"):
        print("👋 Goodbye!")
        break

    # 🔎 Step 1: Query ChromaDB
    results = collection.query(query_texts=[user_query], n_results=5)
    metadatas = results.get("metadatas", [[]])[0]

    if not metadatas:
        print("❌ No matching documents found.\n" + "-" * 60)
        continue

    # 🧠 Step 2: Build context
    context = format_context(metadatas)

    # 🗣️ Step 3: Prompt template
    prompt = f"""You are a helpful assistant that knows about trailer products.

Here are the most relevant trailer parts:

{context}

Now answer the following question based only on the information above:

User Question: {user_query}

Answer:"""

    # 🤖 Step 4: Ask LLaMA
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
        if response.status_code == 200:
            answer = response.json().get("response", "").strip()
            print(f"\n🤖 LLaMA 3: {answer}\n")
        else:
            print(f"❌ Error from LLaMA 3: {response.status_code}\n")
    except Exception as e:
        print(f"❌ Exception while calling LLaMA: {e}\n")

    print("-" * 60)
