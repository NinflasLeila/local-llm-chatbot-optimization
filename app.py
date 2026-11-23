
import streamlit as st
import ollama

from modules.conversation import (
    initialize_conversations,
    create_conversation,
    get_active_conversation,
    add_message,
    delete_conversation,
    export_conversation_json,
    export_conversation_txt
)

# ==========================================
# 1. CONFIGURATION DE L'APPLICATION
# ==========================================

st.set_page_config(
    page_title="ENSET LLM Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 ENSET Chatbot")
st.caption("Assistant conversationnel basé sur des LLMs locaux avec Ollama")

# ==========================================
# 2. INITIALISATION
# ==========================================

initialize_conversations()

# ==========================================
# 3. CONFIGURATION DES MODÈLES
# ==========================================

st.sidebar.header("⚙️ Configuration")

# Détection dynamique des modèles installés
try:
    installed_models = ollama.list()
    available_models = [
        model.model for model in installed_models.models
    ]
except Exception:
    available_models = []
    st.sidebar.error("Service Ollama inaccessible.")

if available_models:
    selected_model = st.sidebar.selectbox(
        "Modèle LLM",
        available_models
    )
else:
    selected_model = None
    st.sidebar.warning("Aucun modèle disponible.")

temperature = st.sidebar.slider(
    "Température",
    0.0, 2.0, 0.7, 0.1
)

top_k = st.sidebar.slider(
    "Top-k", 1, 100, 40
)

top_p = st.sidebar.slider(
    "Top-p", 0.0, 1.0, 0.9, 0.05
)

max_tokens = st.sidebar.slider(
    "Nombre maximal de tokens",
    1, 2048, 512
)

# ==========================================
# 4. GESTION DES CONVERSATIONS
# ==========================================

st.sidebar.divider()
st.sidebar.header("💬 Mes conversations")

if st.sidebar.button(
    "➕ Nouvelle conversation",
    use_container_width=True
):
    create_conversation()
    st.rerun()

conversations = st.session_state.conversations

if conversations:

    conversation_ids = list(conversations.keys())

    # Sélection de la conversation active
    active_id = st.session_state.active_conversation

    if active_id not in conversation_ids:
        active_id = conversation_ids[0]
        st.session_state.active_conversation = active_id

    selected_id = st.sidebar.selectbox(
        "Historique",
        options=conversation_ids,
        index=conversation_ids.index(active_id),
        format_func=lambda cid: conversations[cid]["title"],
        key="conversation_selector"
    )

    if selected_id != st.session_state.active_conversation:
        st.session_state.active_conversation = selected_id
        st.rerun()

    active_conversation = get_active_conversation()

    # Export de la conversation
    if active_conversation:

        st.sidebar.markdown("### 📥 Exporter")

        col1, col2 = st.sidebar.columns(2)

        with col1:
            st.download_button(
                "TXT",
                data=export_conversation_txt(selected_id),
                file_name="conversation.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            st.download_button(
                "JSON",
                data=export_conversation_json(selected_id),
                file_name="conversation.json",
                mime="application/json",
                use_container_width=True
            )

        # Suppression
        if st.sidebar.button(
            "🗑️ Supprimer cette conversation",
            use_container_width=True
        ):
            delete_conversation(selected_id)
            st.rerun()

else:
    st.sidebar.info("Aucune conversation. Commencez-en une nouvelle.")

# ==========================================
# 5. AFFICHAGE DE LA CONVERSATION
# ==========================================

active_conversation = get_active_conversation()

if active_conversation:

    st.subheader(active_conversation["title"])

    for message in active_conversation["messages"]:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ======================================
    # 6. ENVOI D'UN MESSAGE
    # ======================================

    prompt = st.chat_input("Posez votre question...")

    if prompt:

        if not selected_model:
            st.error("Aucun modèle Ollama disponible.")

        else:
            # Ajouter la question
            add_message("user", prompt)

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):

                response_placeholder = st.empty()
                full_response = ""

                try:
                    messages = [
                        {
                            "role": message["role"],
                            "content": message["content"]
                        }
                        for message in get_active_conversation()["messages"]
                    ]

                    with st.spinner("Le modèle génère une réponse..."):

                        for response in ollama.chat(
                            model=selected_model,
                            messages=messages,
                            options={
                                "temperature": temperature,
                                "top_k": top_k,
                                "top_p": top_p,
                                "num_predict": max_tokens
                            },
                            stream=True
                        ):

                            full_response += response.message.content or ""

                            response_placeholder.markdown(
                                full_response + "▌"
                            )

                    response_placeholder.markdown(full_response)

                    add_message("assistant", full_response)

                except Exception as error:

                    st.error(
                        f"Erreur pendant la génération : {error}"
                    )

            st.rerun()

else:
    st.info(
        "👈 Cliquez sur « Nouvelle conversation » "
        "dans la barre latérale pour commencer."
    )

