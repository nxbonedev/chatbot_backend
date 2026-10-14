import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.llm import llm, embedding
from backend.system_prompt import system_prompt

load_dotenv()
INDEX_PATH = Path(os.getenv("INDEX_PATH", str(Path(__file__).resolve().parent.parent / "faiss_multipage_index")))

async def query(prompt: str, history: list[dict] | None = None) -> str:
    history = history or []
    if not INDEX_PATH.exists():
        return "The knowledge base has not been created yet. Call POST /ingest with a website URL first."
    vectorstore = FAISS.load_local(
        str(INDEX_PATH), embedding, allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    documents = await retriever.ainvoke(prompt)
    context = "\n\n".join(document.page_content for document in documents)
    prompt_temp = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ])
    # MessagesPlaceholder expects message tuples or message objects, not DB dicts.
    chat_history = [(item["role"], item["content"]) for item in history if item.get("role") in ("user", "assistant")]
    formatted = prompt_temp.format_messages(input=prompt, context=context, history=chat_history)
    answer = await llm.ainvoke(formatted)
    return answer.content if isinstance(answer.content, str) else str(answer.content)
