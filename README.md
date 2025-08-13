# Sasken-RAG-based-Trailer-Parts-Finder
**🚚 Smart Trailer Parts Finder:** (RAG-based Search & Chatbot)(RAG + Streamlit + Web Scraping)
Smart Trailer Parts Finder is a complete Retrieval-Augmented Generation (RAG) system for finding and querying trailer parts from multiple online sources.
It integrates web scraping, data processing, semantic search, and an LLM-powered chatbot into one streamlined pipeline, accessible through a Streamlit interface.
It integrates live web scraping, data normalization, vector embeddings, and LLaMA 3 responses via Ollama.

✨ Features
1. Automated Web Scraping:
Scrapes trailer part listings from eBay and TrailerPartsUnlimited using Selenium.
Captures title, price, source link, and product image.

2. Data Normalization & Processing:
Merges scraped data from multiple sources.
Cleans and standardizes fields for consistency.

3. Semantic Search with ChromaDB:
Creates vector embeddings via SentenceTransformers (all-MiniLM-L6-v2).
Stores data in ChromaDB for fast similarity search.

4. RAG Chatbot with LLaMA 3 (Ollama):
Retrieves the most relevant product details from ChromaDB.
Uses LLaMA 3 to answer queries based on retrieved data.

5. Interactive Web Interface:
Product Search – Find products by keyword, view details (price, image, source).
Chatbot – Ask product-related questions and get conversational answers.
Secure Login – Restrict access with authentication.
Manual Pipeline Trigger – Run the entire update pipeline from the UI.

## 📂 Project Structure
├── Scrapers/
│ ├── scrape_ebay.py
│ └── scrape_trailerpartsunlimited.py
│
├── rag_engine/
│ ├── 1merge_and_normalize.py
│ ├── 2chunking.py
│ ├── 3embed_to_chromadb.py
│ ├── 4query_from_chromadb.py
│ └── 5RAG_chatbot.py
│
├── chromadb/ # Persistent vector store
├── data/ # Product JSON/CSV and chunks
├── logs/ # Scraper logs
├── ui.py # Streamlit frontend
├── requirements.txt
└── README.md
## ⚙️ Installation
 1. Install dependencies:
    pip install -r requirements.txt
  
 2. Run scrapers (save output in `data/`):
    python Scrapers/scrape_ebay.py
    python Scrapers/scrape_trailerpartsunlimited.py
   
 3. Merge, chunk, embed:
    python rag_engine/1merge_and_normalize.py
    python rag_engine/2chunking.py
    python rag_engine/3embed_to_chromadb.py

 4. Search interface(query from chromaDb)
    python  rag_engine/4query_from_chromadb.py

 5. RAG chatbot
    python  rag_engine/5RAG_chatbot.py

 6. Start Streamlit UI:
    streamlit run ui.py
 
 Default login: `admin` / `password123`


