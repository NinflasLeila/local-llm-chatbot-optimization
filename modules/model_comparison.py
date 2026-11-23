
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
    """Enregistre les résultats des benchmarks dans un CSV."""

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
        "wall_time",
        "cpu_avg_percent",
        "cpu_max_percent",
        "ram_avg_percent",
        "ram_max_percent",
        "ram_max_mb"
    ]

    file_exists = RESULTS_FILE.exists()

    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)

        if not file_exists:
            writer.writeheader()

        for result in results:
            if not result.get("success"):
                continue

            resources = result.get("resources", {})

            row = {
                "timestamp": datetime.now().isoformat(),
                "model": result["model"],
                "question": result["question"],
                "total_duration": result.get("total_duration", 0),
                "generation_duration": result.get("generation_duration", 0),
                "load_duration": result.get("load_duration", 0),
                "ttft": result.get("ttft"),
                "eval_count": result.get("eval_count", 0),
                "prompt_eval_count": result.get("prompt_eval_count", 0),
                "tokens_per_second": result.get("tokens_per_second", 0),
                "wall_time": result.get("wall_time", 0),
                "cpu_avg_percent": resources.get("cpu_avg_percent", 0),
                "cpu_max_percent": resources.get("cpu_max_percent", 0),
                "ram_avg_percent": resources.get("ram_avg_percent", 0),
                "ram_max_percent": resources.get("ram_max_percent", 0),
                "ram_max_mb": resources.get("ram_max_mb", 0)
            }

            writer.writerow(row)


def display_benchmark_results(results):
    """Affiche les réponses, les performances et les ressources."""

    successful_results = [
        result for result in results
        if result.get("success")
    ]

    failed_results = [
        result for result in results
        if not result.get("success")
    ]

    for result in failed_results:
        st.error(
            f"Erreur avec {result['model']} : "
            f"{result.get('error', 'Erreur inconnue')}"
        )

    if not successful_results:
        st.warning("Aucun benchmark réussi.")
        return

    st.subheader("Résultats des modèles")

    col1, col2 = st.columns(2)

    for index, result in enumerate(successful_results):
        column = col1 if index == 0 else col2

        with column:
            st.markdown(f"### {result['model']}")
            st.write(result["response"])

    st.subheader("Métriques de performance")

    performance_df = pd.DataFrame(
        format_benchmark_results(successful_results)
    )

    st.dataframe(
        performance_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Comparaison des performances")

    col1, col2 = st.columns(2)

    with col1:
        fig_time = px.bar(
            performance_df,
            x="Modèle",
            y="Temps total (s)",
            title="Temps total de réponse"
        )

        st.plotly_chart(fig_time, use_container_width=True)

    with col2:
        fig_speed = px.bar(
            performance_df,
            x="Modèle",
            y="Tokens/seconde",
            title="Vitesse de génération"
        )

        st.plotly_chart(fig_speed, use_container_width=True)

    # Monitoring CPU et RAM
    st.subheader("Consommation des ressources")

    resource_rows = []

    for result in successful_results:
        resources = result.get("resources", {})

        resource_rows.append({
            "Modèle": result["model"],
            "CPU moyen (%)": resources.get("cpu_avg_percent", 0),
            "CPU maximum (%)": resources.get("cpu_max_percent", 0),
            "RAM moyenne (%)": resources.get("ram_avg_percent", 0),
            "RAM maximum (%)": resources.get("ram_max_percent", 0),
            "RAM maximale (MB)": resources.get("ram_max_mb", 0)
        })

    resource_df = pd.DataFrame(resource_rows)

    st.dataframe(
        resource_df,
        use_container_width=True,
        hide_index=True
    )

    col1, col2 = st.columns(2)

    with col1:
        fig_cpu = px.bar(
            resource_df,
            x="Modèle",
            y="CPU moyen (%)",
            title="CPU moyen consommé"
        )

        st.plotly_chart(fig_cpu, use_container_width=True)

    with col2:
        fig_ram = px.bar(
            resource_df,
            x="Modèle",
            y="RAM maximale (MB)",
            title="RAM maximale utilisée"
        )

        st.plotly_chart(fig_ram, use_container_width=True)

    # Export des résultats affichés
    csv_data = performance_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Télécharger les résultats CSV",
        data=csv_data,
        file_name="benchmark_results.csv",
        mime="text/csv"
    )


def compare_models(available_models, generation_options):
    """Interface de comparaison de deux modèles Ollama."""

    st.header("Comparaison des modèles LLM")

    if len(available_models) < 2:
        st.warning(
            "Il faut au moins deux modèles Ollama installés."
        )
        return

    default_a = (
        available_models.index("llama3.2:latest")
        if "llama3.2:latest" in available_models
        else 0
    )

    default_b = (
        available_models.index("qwen:0.5b")
        if "qwen:0.5b" in available_models
        else 1
    )

    col1, col2 = st.columns(2)

    with col1:
        model_a = st.selectbox(
            "Premier modèle",
            available_models,
            index=default_a
        )

    with col2:
        model_b = st.selectbox(
            "Deuxième modèle",
            available_models,
            index=default_b
        )

    question = st.text_area(
        "Question à envoyer aux deux modèles",
        placeholder="Saisis ta question ici..."
    )

    if model_a == model_b:
        st.warning("Sélectionne deux modèles différents.")
        return

    if st.button("Lancer le benchmark", type="primary"):

        if not question.strip():
            st.warning("Veuillez saisir une question.")
            return

        results = []

        for model in [model_a, model_b]:

            with st.spinner(f"Évaluation de {model}..."):

                result = benchmark_model(
                    model_name=model,
                    question=question,
                    generation_options=generation_options
                )

                results.append(result)

        save_benchmark_results(results)

        st.session_state["last_comparison"] = results

    if "last_comparison" in st.session_state:
        display_benchmark_results(
            st.session_state["last_comparison"]
        )
