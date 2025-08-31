import time
import re
import random

def _split_numbered_response(section: str, combined_response: str, questions: list[str]) -> list[dict]:
    parts = re.split(r"^\s*(\d+)\.\s*", combined_response, flags=re.MULTILINE)
    results = []
    for i in range(1, len(parts), 2):
        try:
            idx = int(parts[i]) - 1
            q = questions[idx] if 0 <= idx < len(questions) else "[Pregunta no encontrada]"
            ans = parts[i + 1].strip() if i + 1 < len(parts) else ""
        except (ValueError, IndexError):
            q = "[Error al procesar pregunta]"
            ans = parts[i + 1].strip() if i + 1 < len(parts) else ""
        results.append({"section": section, "question": q, "answer": ans})

    if not results:
        for j, q in enumerate(questions):
            if j == 0:
                results.append({"section": section, "question": q, "answer": combined_response.strip()})
            else:
                results.append({"section": section, "question": q, "answer": "No hay información en el documento"})
    return results


def _sleep_with_jitter(base: float):
    time.sleep(base + random.uniform(0, base * 0.25))


def ask_questions(
    client,
    assistant_id: str,
    questions: dict[str, list[str]],
    doc_text: str,
    per_section_timeout_sec: int = 480,      # ↑ más ventana (8 min)
    initial_poll_interval_sec: float = 1.5,
    max_poll_interval_sec: float = 6.0,
    max_chars_context: int = 80_000,        # ajusta según tu deployment
    max_retries_rate: int = 3,              # reintentos por rate limit
    pause_between_sections_sec: float = 2.0 # pausa entre secciones
) -> list[dict]:
    thread = client.beta.threads.create()
    print(f"Created thread: {thread.id}")

    # Inyectar documento como contexto del hilo
    safe_text = doc_text[:max_chars_context]
    print(f"  Injecting ~{len(safe_text)} chars of document into thread context.")
    context_msg = (
        "Contenido del documento a analizar (no inventes información; si no encuentras algo di exactamente: "
        "\"No hay información en el documento\").\n\n"
        "----- INICIO DEL DOCUMENTO -----\n"
        f"{safe_text}\n"
        "----- FIN DEL DOCUMENTO -----"
    )
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=context_msg,
    )

    all_results: list[dict] = []

    for section, section_questions in questions.items():
        print(f"Processing section: {section}")

        lines = [
            f"Responde las siguientes preguntas de la sección '{section}' de forma numerada (1., 2., ...).",
            "Usa exclusivamente el documento que te compartí en este hilo como fuente.",
            "Si alguna pregunta no tiene evidencia en el documento, responde exactamente: \"No hay información en el documento\".",
            "",
        ]
        for i, q in enumerate(section_questions, start=1):
            lines.append(f"{i}. {q}")
        combined_prompt = "\n".join(lines)

        # Publica el mensaje de usuario con las preguntas
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=combined_prompt,
        )

        # Ejecuta el run con reintentos por rate limit
        attempt = 0
        run_id = None
        while attempt <= max_retries_rate:
            attempt += 1
            try:
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant_id,
                )
                run_id = run.id
            except Exception as e:
                # fallback por si el create cae por 429 inmediatamente
                msg = str(e)
                if "rate_limit" in msg or "429" in msg:
                    wait = 20 * attempt
                    print(f"  Create run rate-limited on attempt {attempt}. Waiting {wait}s...")
                    _sleep_with_jitter(wait)
                    continue
                raise

            # Poll con timeout y backoff
            start = time.time()
            poll_interval = initial_poll_interval_sec
            last_status = None
            rate_limited_and_retry = False

            while True:
                status_obj = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run_id)
                status = getattr(status_obj, "status", None)
                if status != last_status:
                    print(f"  Run status for '{section}': {status}")
                    last_status = status

                if status == "completed":
                    break

                if status in ("failed", "cancelled", "expired"):
                    err = getattr(status_obj, "last_error", None)
                    code = getattr(err, "code", None) if err else None
                    message = getattr(err, "message", None) if err else None
                    print(f"  Run ended early for '{section}'. Full error object:")
                    print(f"    last_error: {err}")
                    if code == "rate_limit_exceeded":
                        # Respeta Retry-After si viene en mensaje
                        wait = 30 * attempt
                        # Mensajes tipo "Try again in 40 seconds."
                        if isinstance(message, str):
                            import re
                            m = re.search(r"(\d+)\s*second", message)
                            if m:
                                wait = int(m.group(1))
                        print(f"  Rate limit on polling. Waiting {wait}s and retrying section (attempt {attempt}/{max_retries_rate})...")
                        _sleep_with_jitter(wait)
                        rate_limited_and_retry = True
                    else:
                        # Cualquier otro error: devolvemos “No hay info…”
                        for q in section_questions:
                            all_results.append({
                                "section": section,
                                "question": q,
                                "answer": f"No hay información en el documento ({message or status})."
                            })
                    break

                if status == "requires_action":
                    print(f"  Run requires action for '{section}' but no tools are enabled.")
                    for q in section_questions:
                        all_results.append({"section": section, "question": q,
                                            "answer": "No hay información en el documento (requires_action sin tools)."})
                    break

                elapsed = time.time() - start
                if elapsed > per_section_timeout_sec:
                    print(f"  Timeout reached for '{section}' after {int(elapsed)}s. Cancelling run.")
                    try:
                        client.beta.threads.runs.cancel(thread_id=thread.id, run_id=run_id)
                    except Exception:
                        pass
                    # marcamos como reintento por timeout una sola vez si hay margen
                    if attempt < max_retries_rate:
                        wait = 15 * attempt
                        print(f"  Retrying section '{section}' after timeout. Waiting {wait}s...")
                        _sleep_with_jitter(wait)
                        rate_limited_and_retry = True
                    else:
                        for q in section_questions:
                            all_results.append({"section": section, "question": q, "answer": "No hay información en el documento (timeout)."})
                    break

                time.sleep(poll_interval)
                poll_interval = min(poll_interval * 1.5, max_poll_interval_sec)

            if last_status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread.id, order="desc", limit=10)
                assistant_msg_text = None
                for m in messages.data:
                    try:
                        if m.role == "assistant" and m.content and len(m.content) > 0:
                            assistant_msg_text = m.content[0].text.value
                            break
                    except Exception:
                        continue

                if not assistant_msg_text:
                    for q in section_questions:
                        all_results.append({"section": section, "question": q,
                                            "answer": "No hay información en el documento (sin respuesta del modelo)."})
                else:
                    all_results.extend(_split_numbered_response(section, assistant_msg_text, section_questions))
                break  # sección resuelta, salimos del bucle de reintentos

            if not rate_limited_and_retry:
                # No fue rate limit ni timeout reintetable → no reintentamos
                break

        # pequeña pausa entre secciones para aliviar ritmo
        time.sleep(pause_between_sections_sec)

    return all_results