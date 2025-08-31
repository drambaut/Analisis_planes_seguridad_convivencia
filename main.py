import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
import httpx

from assistants.assistant_manager import get_or_create_assistant
from assistants.question_asker import ask_questions
from config.questions import questions

# Directories
INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Assistant metadata
ASSISTANT_NAME = "DocumentAnalysisAssistant"
ASSISTANT_INSTRUCTIONS = (
    "Eres un asistente experto en el análisis de documentos técnicos. "
    "Debes responder exclusivamente con la información contenida en el documento cargado. "
    "No puedes inventar, asumir ni completar respuestas por fuera del contenido. "
    "Si no encuentras la información necesaria en el documento, responde exactamente: "
    "\"No hay información en el documento\". "
    "Evita especulaciones y no reformules la pregunta. "
    "Tus respuestas deben ser claras, concretas y basadas únicamente en el texto disponible."
)
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-2")

# Throttling between documents to avoid rate limits
COOL_DOWN_BETWEEN_DOCS_SEC = float(os.getenv("COOL_DOWN_BETWEEN_DOCS_SEC", "5"))

def build_client() -> AzureOpenAI:
    load_dotenv()
    # SSL verify disabled (corporate proxy/self-signed environments)
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        http_client=httpx.Client(verify=False),
    )

def process_document(client: AzureOpenAI, assistant_id: str, document_path: Path) -> None:
    print(f"Found document: {document_path.name}")

    try:
        doc_text = document_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Failed to read document '{document_path.name}': {e}")
        return

    # Ask grouped-by-section and split answers per question (handled inside ask_questions)
    responses = ask_questions(
        client=client,
        assistant_id=assistant_id,
        questions=questions,
        doc_text=doc_text,
        # You can tweak these if needed:
        # per_section_timeout_sec=480,
        # max_chars_context=80000,
        # max_retries_rate=3,
    )

    # Save responses to JSON based on input filename stem
    output_filename = f"{document_path.stem}_responses.json"
    output_path = OUTPUT_DIR / output_filename
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2, ensure_ascii=False)
        print(f"Responses saved to: {output_path}")
    except Exception as e:
        print(f"Failed to write output JSON for '{document_path.name}': {e}")

def main():
    client = build_client()

    # Create or reuse the assistant ONCE (reuse across all documents)
    assistant_id = get_or_create_assistant(
        client,
        ASSISTANT_NAME,
        ASSISTANT_INSTRUCTIONS,
        MODEL_NAME,
    )

    # Collect all .txt files
    txt_files = sorted(INPUT_DIR.glob("*.txt"))
    if not txt_files:
        print("No .txt documents found in data/input.")
        return

    total = len(txt_files)
    print(f"Discovered {total} .txt documents.")

    for idx, document_path in enumerate(txt_files, start=1):
        print(f"\n[{idx}/{total}] Processing: {document_path.name}")
        process_document(client, assistant_id, document_path)

        # Optional: skip cooldown after last document
        if idx < total and COOL_DOWN_BETWEEN_DOCS_SEC > 0:
            print(f"Cooling down for {COOL_DOWN_BETWEEN_DOCS_SEC:.1f}s to avoid rate limits...")
            time.sleep(COOL_DOWN_BETWEEN_DOCS_SEC)

if __name__ == "__main__":
    main()