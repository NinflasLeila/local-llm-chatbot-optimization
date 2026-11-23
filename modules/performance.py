
import time
import ollama


def get_value(obj, key, default=None):
    """Récupère une valeur depuis un objet Ollama ou un dictionnaire."""

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def benchmark_model(
    model_name,
    question,
    generation_options
):
    """
    Exécute un benchmark réel d'un modèle Ollama.

    Mesures :
    - Temps total
    - TTFT
    - Tokens générés
    - Temps de génération
    - Tokens par seconde
    - Temps de chargement
    """

    start_time = time.perf_counter()

    first_token_time = None
    full_response = ""

    final_stats = None

    try:

        stream = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
            options=generation_options,
            stream=True,
            keep_alive="5m"
        )

        for chunk in stream:

            current_content = get_value(
                get_value(chunk, "message", {}),
                "content",
                ""
            ) or ""

            # Mesure du premier fragment de réponse
            if current_content and first_token_time is None:
                first_token_time = time.perf_counter()

            full_response += current_content

            # Le dernier événement contient les statistiques
            if get_value(chunk, "done", False):
                final_stats = chunk

        end_time = time.perf_counter()

        if final_stats is None:
            raise RuntimeError(
                "Ollama n'a pas retourné les statistiques finales."
            )

        # Statistiques retournées par Ollama (nanosecondes)
        eval_count = get_value(final_stats, "eval_count", 0) or 0

        eval_duration_ns = (
            get_value(final_stats, "eval_duration", 0) or 0
        )

        total_duration_ns = (
            get_value(final_stats, "total_duration", 0) or 0
        )

        load_duration_ns = (
            get_value(final_stats, "load_duration", 0) or 0
        )

        prompt_eval_count = (
            get_value(final_stats, "prompt_eval_count", 0) or 0
        )

        # Conversion en secondes
        total_duration = total_duration_ns / 1_000_000_000

        generation_duration = eval_duration_ns / 1_000_000_000

        load_duration = load_duration_ns / 1_000_000_000

        # Mesure du TTFT
        if first_token_time is not None:
            ttft = first_token_time - start_time
        else:
            ttft = None

        # Calcul de la vitesse
        if generation_duration > 0:
            tokens_per_second = eval_count / generation_duration
        else:
            tokens_per_second = 0

        # Durée murale mesurée par Python
        wall_time = end_time - start_time

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
            "wall_time": wall_time
        }

    except Exception as error:

        return {
            "success": False,
            "model": model_name,
            "question": question,
            "error": str(error)
        }


def format_benchmark_results(results):
    """Prépare les résultats pour leur affichage."""

    formatted_results = []

    for result in results:

        if not result["success"]:
            continue

        formatted_results.append({
            "Modèle": result["model"],
            "Temps total (s)": round(
                result["total_duration"], 3
            ),
            "TTFT (s)": (
                round(result["ttft"], 3)
                if result["ttft"] is not None else None
            ),
            "Tokens générés": result["eval_count"],
            "Temps génération (s)": round(
                result["generation_duration"], 3
            ),
            "Vitesse (tokens/s)": round(
                result["tokens_per_second"], 2
            ),
            "Chargement (s)": round(
                result["load_duration"], 3
            )
        })

    return formatted_results
