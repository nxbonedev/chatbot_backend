from backend.web_query import query
from backend import db

db.init_db()

async def prompt(question: str, session_id: str | None = None, parent_id: str | None = None) -> dict:
    if not question or not question.strip():
        return {"answer": "Please provide a question."}
    if session_id is None or not db.session_exists(session_id):
        session_id = db.create_session(title=question[:60], s_id=session_id)
        parent_id = None
    if parent_id is None or not db.message_exists(parent_id):
        parent_id = db.latest_leaf(session_id)
    history = db.get_branch(parent_id)
    user_msg_id = db.add_message(session_id, "user", question, parent_id)
    answer = str(await query(prompt=question, history=history))
    assistant_msg_id = db.add_message(session_id, "assistant", answer, user_msg_id)
    return {
        "answer": answer,
        "session_id": session_id,
        "user_message_id": user_msg_id,
        "assistant_message_id": assistant_msg_id,
    }
