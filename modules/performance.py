
import time
import ollama

from modules.monitoring import ResourceMonitor


def get_value(obj, key, default=None):
    """Récupère une valeur depuis un dictionnaire ou un objet."""
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def benchmark_model(model_name, question, generation_options):
    """Exécute un benchmark et mesure les performances du modèle."""

    start_time = time.perf_counter()
    first_token_time = None
    full_response = ""
    final_stats = None

    monitor = ResourceMonitor(interval=0.5)
    monitor.start()

    try:
        stream = ollama.chat(
            model=model_name,
            messages=[
                {"role": "user", "content": question}
            ],
            options=generation_options,
            stream=True,
            keep_alive="5m"
        )

        for chunk in stream:
            message = get_value(chunk, "message", {})
            current_content = get_value(
                message, "content", ""
            ) or ""

            if current_content and first_token_time is None:
                first_token_time = time.perf_counter()

            full_response += current_content

            if get_value(chunk, "done", False):
                final_stats = chunk

        end_time = time.perf_counter()

        if final_stats is None:
            raise RuntimeError(
                "Les statistiques finales Ollama sont absentes."
            )

        # Statistiques fournies par Ollama
        eval_count = get_value(final_stats, "eval_count", 0) or 0
        eval_duration_ns = get_value(
            final_stats, "eval_duration", 0
        ) or 0

        total_duration_ns = get_value(
            final_stats, "total_duration", 0
        ) or 0

        load_duration_ns = get_value(
            final_stats, "load_duration", 0
        ) or 0

        prompt_eval_count = get_value(
            final_stats, "prompt_eval_count", 0
        ) or 0

        # Conversion nanosecondes vers secondes
        total_duration = total_duration_ns / 1e9
        generation_duration = eval_duration_ns / 1e9
        load_duration = load_duration_ns / 1e9

        # Temps avant le premier fragment reçu
        ttft = None

        if first_token_time is not None:
            ttft = first_token_time - start_time

        # Vitesse de génération
        tokens_per_second = 0

        if generation_duration > 0:
            tokens_per_second = eval_count / generation_duration

        wall_time = end_time - start_time

        # Mesures CPU et RAM
        resource_metrics = monitor.stop()

        return {
            "success": True,
            "model": model_name,
            "question": question,
            "response": full_response,
            "total_duration": total_duration,
            "generation_duration": generation_duration,
            "load_duration": load_duration,
            "ttft": ttft,
            "eval_count": eval_count,
            "prompt_eval_count": prompt_eval_count,
            "tokens_per_second": tokens_per_second,
            "wall_time": wall_time,
            "resources": resource_metrics
        }

    except Exception as error:
        resource_metrics = monitor.stop()

        return {
            "success": False,
            "model": model_name,
            "question": question,
            "error": str(error),
            "resources": resource_metrics
        }


def format_benchmark_results(results):
    """Prépare les résultats pour leur affichage dans Streamlit."""

    formatted_results = []

    for result in results:
        formatted_results.append({
            "Modèle": result["model"],
            "Temps total (s)": round(
                result.get("total_duration", 0), 2
            ),
            "TTFT (s)": (
                round(result["ttft"], 2)
                if result.get("ttft") is not None
                else "N/A"
            ),
            "Tokens générés": result.get("eval_count", 0),
            "Temps génération (s)": round(
                result.get("generation_duration", 0), 2
            ),
            "Tokens/seconde": round(
                result.get("tokens_per_second", 0), 2
            ),
            "Temps chargement (s)": round(
                result.get("load_duration", 0), 2
            )
        })

    return formatted_results

