def compact_context(documents: list, stop_words: set = None) -> str:
    """Compacts retrieved LangChain documents to increase token density."""
    if stop_words is None:
        # Basic filler words that models don't need for semantic understanding
        stop_words = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "is", "are", "of", "it", "that", "this", "we", "do"}
    
    compacted_chunks = []
    
    # Process each FAISS document chunk
    for index, doc in enumerate(documents):
        # Strip excess whitespace and remove common stop words
        words = doc.page_content.split()
        dense_text = " ".join([word for word in words if word.lower() not in stop_words])
        
        # Append with structural brackets so the LLM can differentiate chunks
        compacted_chunks.append(f"[{index}] {dense_text}")
        
    return "\n\n".join(compacted_chunks)