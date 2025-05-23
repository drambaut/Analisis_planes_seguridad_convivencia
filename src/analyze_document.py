import os
import json
from openai import AzureOpenAI
import pandas as pd
from pathlib import Path
from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    DATA_DIR,
    OUTPUT_DIR,
    TEMPERATURE,
    MAX_TOKENS
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Questions structure
questions = {
    "INFORMACIÓN GENERAL": [
        "¿Qué tipos existen?",
        "Departamento",
        "Código DANE",
        "Nombre del Plan",
        "Período de referencia",
        "Entidades que presentan el documento",
        "Autoridades que participaron en la elaboración",
        "¿El documento cuenta con Diagnóstico?",
        "¿El documento cuenta con Formulación?",
        "¿El documento cuenta con Planeación Financiera?",
        "¿El documento cuenta con Planeación Operativa?",
        "¿El documento cuenta con implementación?",
        "¿El documento cuenta con seguimiento?",
        "¿El documento cuenta con evaluación?",
        "Fecha de elaboración del PISCC"
    ],
    "DIAGNÓSTICO": [
        "¿La sección de diagnóstico sigue la estructura establecida en la guía?",
        "¿La sección de diagnóstico incluye la identificación de factores de riesgo?",
        "¿La sección de diagnóstico incluye el diagnóstico de conflictividades?",
        "¿La sección de diagnóstico incluye el análisis de alertas tempranas?",
        "¿La sección de diagnóstico incluye el análisis de comportamientos contrarios a la convivencia?",
        "¿La sección de diagnóstico incluye el análisis de los delitos?",
        "Análisis desagregado de factores de riesgo en función de las dimensiones de la seguridad humana",
        "Análisis desagregado de delitos contra la vida y la integridad personal",
        "Análisis desagregado de delitos contra la libertad, integridad y orientación sexual",
        "Análisis desagregado de delitos contra la familia",
        "Análisis desagregado de delitos contra el patrimonio económico",
        "Análisis desagregado de delitos contra la salud pública",
        "Análisis desagregado de lesiones muertes en accidentes de tránsito",
        "Análisis desagregado de delitos contra el medio ambiente",
        "¿Se realizó una priorización de problemáticas?",
        "¿Cuáles son las fuentes de información utilizadas para el diagnóstico?",
        "¿Cuáles son las herramientas utilizadas para el análisis de la información?",
        "En años, ¿cuál es el periodo de análisis de la información?",
        "¿El diagnóstico fue elaborado de forma participativa?",
        "¿En este diagnóstico se utiliza árbol de problemas u otra herramienta?"
    ],
    "FORMULACIÓN": [
        "¿Para la formulación del plan se siguió la estructura propuesta en la guía?",
        "¿Para la formulación del plan se incluyó la elaboración de objetivo general?",
        "¿Para la formulación del plan se incluyó la elaboración de objetivos específicos?",
        "¿Para la formulación del plan se incluye la definición de líneas estratégicas o programas?",
        "¿Para la formulación del plan se incluye la definición de proyectos o actividades?",
        "¿Para la formulación del plan se incluye la definición de metas?",
        "¿Para la formulación del plan se incluye la definición de indicadores?",
        "¿Para la formulación del plan se incluyen instrumentos de planeación?",
        "¿Para la formulación del plan se incluyen instrumentos de política?",
        "¿Para la formulación de programas, proyectos y actividades se incluyen los enfoques diferenciales e interseccionales?",
        "Transcribir el objetivo general",
        "Transcribir los objetivos específicos",
        "Transcribir las líneas estratégicas",
        "¿Las líneas estratégicas están asociadas a un objetivo específico?",
        "¿Los proyectos planteados guardan coherencia con las problemáticas priorizadas?",
        "¿Los proyectos y actividades planteadas identifican responsables?",
        "¿Los proyectos propuestos responden a la identificación de productos en el catálogo de la MGA?"
    ],
    "PLANEACIÓN OPERATIVA Y FINANCIERA": [
        "¿Se incluye en la planeación financiera el POAI?",
        "¿Se incluye en el POAI las posibles fuentes de financiación de las líneas estratégicas?",
        "¿Se prevé el uso de algunas de las siguientes fuentes de financiación en la planeación?",
        "¿La asignación de recursos preliminar guarda coherencia con la priorización de problemáticas y de estrategias?"
    ],
    "SEGUIMIENTO Y EVALUACIÓN": [
        "¿En la fase de implementación se contempla la matriz de seguimiento a compromisos?",
        "¿Se contempla una metodología para el seguimiento a la implementación del plan?",
        "¿Se contempla una metodología para evaluar la implementación del plan?",
        "¿Se establece la estructura organizacional para el seguimiento del PISCC?"
    ]
}

def read_document(file_path):
    """Read the content of a text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def analyze_with_gpt(document_content, question):
    """Send a question to Azure OpenAI API and get the response."""
    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "Eres un asistente experto en analizar documentos de planes de seguridad y convivencia ciudadana. Responde de manera concisa y precisa. Si no puedes encontrar la respuesta en el documento, responde 'No hay respuesta'."},
                {"role": "user", "content": f"Documento:\n{document_content}\n\nPregunta: {question}"}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error al procesar la pregunta: {question}")
        print(f"Error: {str(e)}")
        return "Error en el procesamiento"

def process_document(file_path):
    """Process a single document and return results as a DataFrame."""
    print(f"Procesando documento: {file_path}")
    document_content = read_document(file_path)
    
    results = []
    
    for section, section_questions in questions.items():
        for question in section_questions:
            print(f"Procesando pregunta: {question}")
            answer = analyze_with_gpt(document_content, question)
            results.append({
                "Sección": section,
                "Pregunta": question,
                "Respuesta": answer
            })
    
    return pd.DataFrame(results)

def main():
    # Create output directory if it doesn't exist
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    
    # Process first document in data/raw
    raw_dir = Path(DATA_DIR)
    first_doc = next(raw_dir.glob("*.txt"))
    
    # Process document and save results
    df = process_document(first_doc)
    output_file = output_dir / f"analisis_{first_doc.stem}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Resultados guardados en: {output_file}")

if __name__ == "__main__":
    main() 