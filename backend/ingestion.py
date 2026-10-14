import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from backend.web_scaraper import cleanhtml
from backend.llm import embedding

load_dotenv()
INDEX_PATH = Path(os.getenv("INDEX_PATH", str(Path(__file__).resolve().parent.parent / "faiss_multipage_index")))
HEADER = {
    "User-Agent": "Mozilla/5.0 (compatible; ItelChatbot/1.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def ingest_site(base_url: str, max_depth: int = 1, chunk_size: int = 1000, chunk_overlap: int = 150):
    if not base_url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")
    print(f"Crawling website: {base_url} up to depth {max_depth}...")
    loader = RecursiveUrlLoader(
        url=base_url, max_depth=max_depth, extractor=cleanhtml,
        prevent_outside=True, headers=HEADER, timeout=30, use_async=False,
    )
    raw_docs = loader.load()
    if not raw_docs:
        raise ValueError(f"No pages could be scraped from {base_url}")
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    doc_chunks = splitter.split_documents(raw_docs)
    if not doc_chunks:
        raise ValueError(f"No text content could be extracted from {base_url}")
    for idx, chunk in enumerate(doc_chunks):
        chunk.metadata["chunk_index"] = idx
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    vectorstore = FAISS.from_documents(documents=doc_chunks, embedding=embedding)
    vectorstore.save_local(str(INDEX_PATH))
    print(f"Vector index saved to '{INDEX_PATH}'.")
    return len(raw_docs), len(doc_chunks)
