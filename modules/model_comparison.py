
import streamlit as st
import pandas as pd
import plotly.express as px

import csv
from pathlib import Path
from datetime import datetime

from modules.performance import (
    benchmark_model,
    format_benchmark_results
)


RESULTS_FILE = Path("data/experiments/benchmark_results.csv")


def save_benchmark_results(results):
    """Enregistre les mesures expérimentales dans un CSV."""

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "timestamp",
        "model",
        "question",
        "total_duration",
        "generation_duration",
        "load_duration",
        "ttft",
        "eval_count",
        "prompt_eval_count",
        "tokens_per_second",
        "wall_time"
    ]

    file_exists = RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0

    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=columns)

        if not file_exists:
            writer.writeheader()

        for result in results:

            if not result["success"]:
                continue

            writer.writerow({
                "timestamp": datetime.now().isoformat(),
                "model": result["model"],
                "question": result["question"],
                "total_duration": result["total_duration"],
                "generation_duration": result["generation_duration"],
                "load_duration": result["load_duration"],
                "ttft": result["ttft"],
                "eval_count": result["eval_count"],
                "prompt_eval_count": result["prompt_eval_count"],
                "tokens_per_second": result["tokens_per_second"],
                "wall_time": result["wall_time"]
            })


def display_benchmark_results(results):
    """Affiche les réponses et les mesures expérimentales."""

    successful_results = [
        result for result in results if result["success"]
    ]

    failed_results = [
        result for result in results if not result["success"]
    ]

    if failed_results:
        st.warning("Certains modèles n'ont pas terminé leur génération.")

        for result in failed_results:
            st.error(
                f"{result['model']} : {result['error']}"
            )

    if not successful_results:
        st.error("Aucun résultat exploitable.")
        return

    st.divider()
    st.subheader("📊 Résultats de la comparaison")

    # Réponses côte à côte
    columns = st.columns(len(successful_results))

    for column, result in zip(columns, successful_results):

        with column:
            st.markdown(f"### 🤖 {result['model']}")
            st.markdown(result["response"])

    # Tableau comparatif
    st.divider()
    st.subheader("📈 Indicateurs de performance")

    table_data = format_benchmark_results(successful_results)

    df = pd.DataFrame(table_data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # Graphiques
    st.subheader("Visualisation des performances")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        fig_time = px.bar(
            df,
            x="Modèle",
            y="Temps total (s)",
            title="Temps total de réponse",
            text_auto=".2f"
        )

        st.plotly_chart(fig_time, use_container_width=True)

    with chart_col2:

        fig_speed = px.bar(
            df,
            x="Modèle",
            y="Vitesse (tokens/s)",
            title="Vitesse de génération",
            text_auto=".2f"
        )

        st.plotly_chart(fig_speed, use_container_width=True)

    # Export des résultats
    st.download_button(
        label="📥 Télécharger les résultats CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="llm_benchmark.csv",
        mime="text/csv"
    )


def compare_models(available_models, generation_options):

    st.subheader("⚖️ Comparaison de deux modèles LLM")

    if len(available_models) < 2:
        st.warning("Au moins deux modèles sont nécessaires.")
        return

    # Sélection des modèles
    col1, col2 = st.columns(2)

    with col1:
        model_a = st.selectbox(
            "Premier modèle",
            available_models,
            index=(
                available_models.index("llama3.2:latest")
                if "llama3.2:latest" in available_models else 0
            ),
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
        st.warning("Sélectionnez deux modèles différents.")
        return

    st.divider()

    question = st.text_area(
        "Question commune aux deux modèles",
        placeholder="Saisissez votre question...",
        height=120,
        key="comparison_question"
    )

    st.caption(
        "Les modèles sont exécutés séquentiellement "
        "avec des paramètres identiques."
    )

    if st.button(
        "🚀 Lancer le benchmark",
        type="primary",
        use_container_width=True
    ):

        if not question.strip():
            st.warning("Veuillez saisir une question.")
            return

        results = []

        for model_name in [model_a, model_b]:

            st.markdown(f"### Exécution : {model_name}")

            with st.spinner(
                f"Benchmark de {model_name} en cours..."
            ):

                result = benchmark_model(
                    model_name=model_name,
                    question=question,
                    generation_options=generation_options
                )

                results.append(result)

            if result["success"]:
                st.success(
                    f"{model_name} : génération terminée."
                )
            else:
                st.error(
                    f"{model_name} : {result['error']}"
                )

        save_benchmark_results(results)

        st.session_state["last_comparison"] = {
            "question": question,
            "models": [model_a, model_b],
            "results": results,
            "options": generation_options
        }

    # Conserver l'affichage après les reruns Streamlit
    last_comparison = st.session_state.get("last_comparison")

    if last_comparison:

        display_benchmark_results(
            last_comparison["results"]
        )

