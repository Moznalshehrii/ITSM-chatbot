import os
import numpy as np
import pandas as pd
import faiss
from google import genai
from dotenv import load_dotenv

# Load environment
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)

# Models and constants
GENERATION_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "text-embedding-004"
TOP_K = 5
THRESHOLD = 0.50
BATCH_SIZE = 50
DEFAULT_XLSX = "ServiceNow_KB_Dummy_Articles_150.xlsx"

# Prompt for title generation
TITLE_PROMPT = """You are a title normalizer for IT helpdesk tickets.
Create a short, clear title (4–8 words, Title Case) from a long incident description.
Examples:
- Updating Antivirus Definitions
- Printer Offline Error – Quick Fix
- Resetting VPN Access on Windows 11
Return only the title, nothing else.
"""

def load_dataset(xlsx_path=DEFAULT_XLSX):
    df = pd.read_excel(xlsx_path)
    df.columns = df.columns.str.lower().str.strip()
    if "short_desc" in df.columns and "short_description" not in df.columns:
        df.rename(columns={"short_desc": "short_description"}, inplace=True)
    df["short_description"] = df["short_description"].astype(str).str.strip()
    df["text"] = df["text"].astype(str).str.strip()
    return df

def build_index(df):
    texts = df["short_description"].tolist()
    vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i+BATCH_SIZE]
        resp = client.models.embed_content(model=EMBEDDING_MODEL, contents=batch)
        for emb in resp.embeddings:
            vectors.append(np.array(emb.values, dtype=np.float32))
    emb_matrix = np.vstack(vectors)
    faiss.normalize_L2(emb_matrix)
    dim = emb_matrix.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb_matrix)
    return index, dim

def generate_title(text):
    prompt = [
        TITLE_PROMPT,
        f"User incident description:\n{text.strip()}\nReturn ONLY the title:"
    ]
    resp = client.models.generate_content(model=GENERATION_MODEL, contents=prompt)
    return (resp.text or "").strip()

def get_fix(user_text, df, index):
    title = generate_title(user_text)
    emb = client.models.embed_content(model=EMBEDDING_MODEL, contents=title)
    query = np.array(emb.embeddings[0].values, dtype=np.float32).reshape(1, -1)
    faiss.normalize_L2(query)

    scores, idxs = index.search(query, TOP_K)
    best_score = float(scores[0][0])

    if best_score < THRESHOLD:
        return {
            "title": title,
            "score": best_score,
            "matched": None,
            "fix": "Sorry, we don't have an answer for this incident right now. Please contact the IT Help Desk for more information."
        }

    best_row = df.iloc[int(idxs[0][0])]
    return {
        "title": title,
        "score": best_score,
        "matched": best_row["short_description"],
        "fix": best_row["text"]
    }