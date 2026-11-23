import streamlit as st 
import json
import uuid
from datetime import datetime


def initialize_conversations():
    """Initialise le gestionnaire de conversations."""

    if "conversations" not in st.session_state:
        st.session_state.conversations = {}

    if "active_conversation" not in st.session_state:
        st.session_state.active_conversation = None


def create_conversation():
    """Crée une nouvelle conversation."""

    conversation_id = str(uuid.uuid4())

    st.session_state.conversations[conversation_id] = {
        "id": conversation_id,
        "title": "Nouvelle conversation",
        "created_at": datetime.now().isoformat(),
        "messages": []
    }

    st.session_state.active_conversation = conversation_id

    return conversation_id


def get_active_conversation():
    """Retourne la conversation actuellement sélectionnée."""

    conversation_id = st.session_state.active_conversation

    if conversation_id is None:
        return None

    return st.session_state.conversations.get(conversation_id)


def add_message(role, content):
    """Ajoute un message à la conversation active."""

    conversation = get_active_conversation()

    if conversation is None:
        return

    conversation["messages"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

    # Générer automatiquement un titre à partir du premier message.
    if role == "user" and conversation["title"] == "Nouvelle conversation":
        conversation["title"] = content[:40] + (
            "..." if len(content) > 40 else ""
        )


def delete_conversation(conversation_id):
    """Supprime une conversation."""

    if conversation_id in st.session_state.conversations:
        del st.session_state.conversations[conversation_id]

    if st.session_state.active_conversation == conversation_id:
        st.session_state.active_conversation = None


def export_conversation_json(conversation_id):
    """Exporte une conversation au format JSON."""

    conversation = st.session_state.conversations[conversation_id]

    return json.dumps(
        conversation,
        ensure_ascii=False,
        indent=4
    )


def export_conversation_txt(conversation_id):
    """Exporte une conversation au format TXT."""

    conversation = st.session_state.conversations[conversation_id]

    lines = [
        f"Conversation : {conversation['title']}",
        f"Date : {conversation['created_at']}",
        "=" * 50,
        ""
    ]

    for message in conversation["messages"]:
        role = message["role"].upper()
        timestamp = message.get("timestamp", "")

        lines.append(f"[{role}] {timestamp}")
        lines.append(message["content"])
        lines.append("")

    return "\n".join(lines)
