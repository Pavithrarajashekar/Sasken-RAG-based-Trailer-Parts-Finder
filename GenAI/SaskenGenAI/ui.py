import streamlit as st
import chromadb
from chromadb.config import Settings
import requests
import subprocess
from datetime import datetime


# ---------------------------
# Constants / Settings
# ---------------------------
CHROMA_PATH = "chromadb"
COLLECTION_NAME = "trailer_parts"

OLLAMA_MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434/api/generate"


# ---------------------------
# Initialize ChromaDB client and collection (once)
# ---------------------------
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


# ---------------------------
# Authentication helpers
# ---------------------------
VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"


def login(username, password):
    return username == VALID_USERNAME and password == VALID_PASSWORD


def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""


# ---------------------------
# Helper: Format ChromaDB product metadata
# ---------------------------
def format_context(metadatas):
    chunks = []
    for meta in metadatas:
        name = meta.get("name", "No Name")
        price = meta.get("price", "N/A")
        source = meta.get("source_site", "Unknown")
        url = meta.get("url", "#")
        chunks.append(f"- {name}\n  Price: ${price}\n  Source: {source}\n  Link: {url}")
    return "\n\n".join(chunks)


# ---------------------------
# Helper: Get LLaMA response
# ---------------------------
def get_llama_response(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"❌ Error: LLaMA responded with status code {response.status_code}"
    except Exception as e:
        return f"❌ Exception while calling LLaMA: {e}"


# ---------------------------
# Streamlit page config
# ---------------------------
st.set_page_config(page_title="Smart Trailer Parts Finder", page_icon="🔧", layout="wide")

# Inject custom CSS for styling including login form color improvements
st.markdown("""
    <style>
    /* App main background */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #4b4b4b 100%);
        background-size: cover;
        background-attachment: fixed;
        color: #ffffff !important;
    }

    /* Sidebar background and text */
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(135deg, #1a1a1a 0%, #4b4b4b 100%) !important;
        color: #ffffff !important;
        height: 100vh;
        padding: 1rem;
    }
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6 {
        color: #f4f4f4 !important;
        font-weight: bold;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Style containers in main area */
    .stContainer {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        padding: 15px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 10px;
    }

    /* Style buttons */
    .search-type-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 15px !important;
    }
    .stButton>button {
        background-color: #2a2a2a;
        color: #ffffff !important;
        border: 1px solid #ff6200;
        border-radius: 5px;
        padding: 5px 15px !important;
        transition: background-color 0.3s ease, color 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #ff6200;
        color: #ffffff !important;
    }
    .stButton>button.selected {
        background-color: #ff6200;
        color: #ffffff !important;
    }

    /* Style text inputs */
    .stTextInput input {
        background-color: #2a2a2a;
        color: #ffffff !important;
        border: 1px solid #ff6200;
        border-radius: 5px;
        padding: 5px !important;
    }

    .stTextInput input::placeholder {
        color: #cccccc !important;
        opacity: 1;
    }

    /* Style Streamlit feedback messages */
    .stAlert {
        background: rgba(0, 0, 0, 0.5) !important;
        color: #ffffff !important;
        border-radius: 5px;
        padding: 10px !important;
    }

    .stSuccess { background-color: rgba(46, 125, 50, 0.8) !important; }
    .stError { background-color: rgba(211, 47, 47, 0.8) !important; }
    .stWarning { background-color: rgba(237, 108, 2, 0.8) !important; }
    .stInfo { background-color: rgba(2, 136, 209, 0.8) !important; }

    /* Ensure links are visible */
    a {
        color: #ff6200 !important;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
        color: #e05500 !important;
    }

    /* Hover effects for text */
    .stMarkdown h4, .stMarkdown p {
        transition: color 0.3s ease, text-shadow 0.3s ease !important;
    }
    .stMarkdown h4:hover, .stMarkdown p:hover {
        color: #ff9f43 !important;
        text-shadow: 0 0 5px rgba(255, 147, 67, 0.5) !important;
    }

    /* Hover effects for images */
    .stImage img {
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        border-radius: 5px !important;
    }
    .stImage img:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 10px rgba(255, 98, 0, 0.5) !important;
    }

    /* Ensure text in data containers is visible */
    .stText, .stMarkdown p, .stMarkdown div {
        color: #ffffff !important;
    }

    /* ----- Login page specific styles (scoped to #login_form) ----- */
    #login_form .stTextInput > div > div > input,
    #login_form .stTextInput > label {
        color: #ff7f50 !important;  /* warm coral/orange for better contrast */
    }
    #login_form .stTextInput > div > div > input::placeholder {
        color: #ffb07a !important;  /* lighter orange-ish for placeholder */
    }
    #login_form .stButton > button {
        color: #ff7f50 !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------
# SESSION STATE Initialize
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chatbot_input" not in st.session_state:
    st.session_state.chatbot_input = ""
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "search_results" not in st.session_state:
    st.session_state.search_results = None


# ---------------------------
# Sidebar Navigation
# ---------------------------
st.sidebar.title("🔧 Smart Trailer Parts Finder")
menu_option = st.sidebar.radio(
    "Navigate",
    ("Login", "Search Interface", "RAG Chatbot", "Daily Update Pipeline"),
    index=0 if not st.session_state.logged_in else 1,
)

if not st.session_state.logged_in and menu_option != "Login":
    st.sidebar.warning("Please login to access other pages.")
    menu_option = "Login"

if st.session_state.logged_in:
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()


# ---------------------------
# Page: Login
# ---------------------------
if menu_option == "Login":
    st.title("🔐 Login")
    st.markdown('<div id="login_form">', unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        username_in = st.text_input("Username")
        password_in = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if login(username_in, password_in):
            st.session_state.logged_in = True
            st.session_state.username = username_in
            st.success("✅ Successfully logged in!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")


# ---------------------------
# Page: Search Interface
# ---------------------------
if menu_option == "Search Interface" and st.session_state.logged_in:
    st.title("🔍 Trailer Parts Search (via ChromaDB)")
    st.markdown("Enter a keyword to find matching trailer parts from eBay and other sources.")

    user_search_query = st.text_input(
        "🧠 Enter your product search query:",
        value=st.session_state.search_query,
        key="search_query"
    )

    if st.button("Search"):
        if st.session_state.search_query.strip():
            results = collection.query(query_texts=[st.session_state.search_query.strip()], n_results=5)
            st.session_state.search_results = results
        else:
            st.session_state.search_results = None
            st.error("❌ Please enter a valid search query.")

    if st.session_state.search_results:
        results = st.session_state.search_results
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents or not metadatas:
            st.error("❌ No matching products found.")
        else:
            st.success(f"✅ Found {len(documents)} matching products:")

            for i, metadata in enumerate(metadatas):
                name = metadata.get("name", "No title")
                price = metadata.get("price", "N/A")
                url = metadata.get("url", "#")
                source = metadata.get("source_site", "Unknown")
                image_url = metadata.get("image_url", "")

                if not image_url or not image_url.startswith("http"):
                    image_url = "https://via.placeholder.com/150"

                with st.container():
                    st.markdown(f"### 🔹 {name}")
                    st.image(image_url, width=200)
                    st.markdown(f"💰 **Price:** ${price}")
                    st.markdown(f"🌐 **Source:** {source}")
                    st.markdown(f"🔗 [Buy link]({url})")
                    st.markdown("---")


# ---------------------------
# Page: RAG Chatbot
# ---------------------------
def handle_chatbot_input():
    chatbot_query = st.session_state.chatbot_input.strip()
    if chatbot_query:
        results = collection.query(query_texts=[chatbot_query], n_results=5)
        metadatas = results.get("metadatas", [[]])[0]

        if not metadatas:
            bot_response = "❌ No matching products found in the database."
        else:
            context = format_context(metadatas)
            prompt = f"""You are a helpful assistant that knows about trailer products.

Here are the most relevant trailer parts:

{context}

Now answer the following question based only on the information above:

User Question: {chatbot_query}

Answer:"""

            bot_response = get_llama_response(prompt)

        st.session_state.chat_history.append((chatbot_query, bot_response))
        st.session_state.chatbot_input = ""  # This is safe inside on_change callback


if menu_option == "RAG Chatbot" and st.session_state.logged_in:
    st.title("🤖 RAG Chatbot (LLaMA 3 + ChromaDB)")
    st.markdown("Ask any trailer part-related question below:")

    st.text_input(
        "🧠 You:",
        placeholder="Type your question and press Enter...",
        key="chatbot_input",
        on_change=handle_chatbot_input
    )

    if st.session_state.chat_history:
        st.markdown("### 💬 Chat History")
        for q, a in st.session_state.chat_history:
            st.markdown(f"**🧠 You:** {q}")
            st.markdown(f"**🤖 LLaMA 3:** {a}")
            st.markdown("---")


# ---------------------------
# Page: Daily Update Pipeline
# ---------------------------
def run_command(label, command):
    with st.spinner(f"{label}..."):
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            st.error(f"❌ {label} failed.")
            return False
        st.success(f"✅ {label} completed.")
        return True


if menu_option == "Daily Update Pipeline" and st.session_state.logged_in:
    st.title("🔄 Daily Data Update Pipeline")
    st.markdown("This interface lets you manually trigger the daily pipeline to scrape, process, and embed trailer parts data.")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if st.button("🚀 Run Daily Update Pipeline"):
        st.write(f"📅 Started at: `{timestamp}`")

        if not run_command("Running eBay scraper", "python Scrapers/scrape_ebay.py"):
            st.stop()

        if not run_command("Running TrailerPartsUnlimited scraper", "python Scrapers/scrape_trailerpartsunlimited.py"):
            st.stop()

        if not run_command("Merging & normalizing data", "python rag_engine/1merge_and_normalize.py"):
            st.stop()

        if not run_command("Chunking merged data", "python rag_engine/2chunking.py"):
            st.stop()

        if not run_command("Embedding into ChromaDB", "python rag_engine/3embed_to_chromadb.py"):
            st.stop()

        st.success(f"🎉 Pipeline completed successfully at `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
