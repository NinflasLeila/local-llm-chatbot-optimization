
import streamlit as st
import ollama

st.set_page_config(
    page_title="Mon assistant IA",
    page_icon="🤖"
)

st.title("🤖 Mon assistant IA local")
st.write("Application utilisant Ollama et Streamlit")

model = st.selectbox(
    "Choisir un modèle IA",
    ["llama3.2", "qwen:0.5b"]
)

question = st.text_area("Posez votre question :")

if st.button("Envoyer"):
    if question:
        with st.spinner("L'IA réfléchit..."):
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

        st.subheader("Réponse :")
        st.write(response["message"]["content"])
    else:
        st.warning("Veuillez saisir une question.")
