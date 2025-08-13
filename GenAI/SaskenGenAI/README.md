# 🚛 Smart Trailer Parts Finder (RAG + Streamlit + Web Scraping)

This project is a Retrieval-Augmented Generation (RAG) system with a Streamlit web interface for searching and chatting about trailer parts.  
It integrates live web scraping, data normalization, vector embeddings, and LLaMA 3 responses via Ollama.

---

## 📌 Features
- Web Scraping: Extract trailer part listings from eBay and TrailerPartsUnlimited.
- Data Processing: Normalize, merge, and chunk product data.
- Vector Search: Store embeddings in **ChromaDB** for semantic search.
- RAG Chatbot: Use LLaMA 3 to answer questions based on retrieved context.
- Daily Update Pipeline: Trigger scrapers → merge → chunk → embed — all from the UI.
- Login System: Secure access to search and chatbot features.

---

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
├── ui3.py # Streamlit frontend
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

4.Search interface(query from chromaDb)
  python  rag_engine/4query_from_chromadb.py

5.RAG chatbot
  python  rag_engine/5RAG_chatbot.py

   
 4. Start Streamlit UI:
   
   streamlit run ui.py
 
 Default login: `admin` / `password123`