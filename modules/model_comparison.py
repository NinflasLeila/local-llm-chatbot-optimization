
import streamlit as st
import ollama


def compare_models(available_models, generation_options):
    """
    Compare deux modèles Ollama sur une question identique.
    Les appels sont exécutés séquentiellement pour éviter
    une concurrence excessive sur les ressources de la VM.
    """

    st.subheader("⚖️ Comparaison de deux modèles LLM")

    if len(available_models) < 2:
        st.warning(
            "Il faut au moins deux modèles Ollama installés "
            "pour effectuer une comparaison."
        )
        return

    # Sélection des deux modèles
    col1, col2 = st.columns(2)

    with col1:
        model_a = st.selectbox(
            "Premier modèle",
            available_models,
            index=available_models.index("llama3.2:latest")
            if "llama3.2:latest" in available_models else 0,
            key="comparison_model_a"
        )

    with col2:
        default_b = 1 if len(available_models) > 1 else 0

        model_b = st.selectbox(
            "Deuxième modèle",
            available_models,
            index=default_b,
            key="comparison_model_b"
        )

    if model_a == model_b:
        st.warning("Veuillez sélectionner deux modèles différents.")
        return

    st.divider()

    # Question commune
    question = st.text_area(
        "Votre question",
        placeholder="Exemple : Explique le fonctionnement de Apache Spark...",
        height=120,
        key="comparison_question"
    )

    st.caption(
        "Les deux modèles recevront exactement la même question "
        "et les mêmes paramètres de génération."
    )

    # Lancement de la comparaison
    if st.button(
        "🚀 Comparer les modèles",
        type="primary",
        use_container_width=True
    ):

        if not question.strip():
            st.warning("Veuillez saisir une question.")
            return

        results = {}

        # Exécution séquentielle
        for model_name in [model_a, model_b]:

            with st.spinner(f"Le modèle {model_name} génère sa réponse..."):

                try:
                    response = ollama.chat(
                        model=model_name,
                        messages=[
                            {
                                "role": "user",
                                "content": question
                            }
                        ],
                        options=generation_options,
                        stream=False
                    )

                    results[model_name] = {
                        "success": True,
                        "content": response.message.content
                    }

                except Exception as error:

                    results[model_name] = {
                        "success": False,
                        "error": str(error)
                    }

        # Affichage côte à côte
        st.divider()
        st.subheader("📊 Résultats de la comparaison")

        col1, col2 = st.columns(2)

        for column, model_name in zip(
            [col1, col2],
            [model_a, model_b]
        ):

            with column:

                st.markdown(f"### 🤖 {model_name}")

                result = results[model_name]

                if result["success"]:
                    st.success("Génération terminée")
                    st.markdown(result["content"])

                else:
                    st.error(
                        f"Erreur de génération : {result['error']}"
                    )

        # Sauvegarde temporaire des résultats
        st.session_state["last_comparison"] = {
            "question": question,
            "models": [model_a, model_b],
            "results": results,
            "options": generation_options
        }
