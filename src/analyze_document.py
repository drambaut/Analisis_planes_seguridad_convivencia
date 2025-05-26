import os
from openai import OpenAI
import pandas as pd
from pathlib import Path
from config import (
    OPENAI_API_KEY,
    OUTPUT_DIR
)
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# OpenAI configuration
client = OpenAI(
    api_key=OPENAI_API_KEY
)

# Assistant ID
ASSISTANT_ID = "asst_JS37tlMfl3XaB3PpyAIF5ujw"

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

def create_thread():
    """Create a new thread for the conversation."""
    return client.beta.threads.create()

def analyze_with_assistant():
    """Use the assistant to answer questions."""
    try:
        print("Iniciando análisis con el asistente...")
        
        # Create a new thread
        thread = create_thread()
        print("✓ Hilo de conversación creado")
        
        results = []
        
        # Process each section of questions
        for section, section_questions in questions.items():
            print(f"\nProcesando sección: {section}")
            
            # Process each question individually
            for question in section_questions:
                print(f"\nEnviando pregunta: {question}")
                
                # Add question to the thread
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=question
                )
                print("✓ Pregunta enviada")
                
                # Create a new run for the question
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=ASSISTANT_ID
                )
                print("  Esperando respuesta del asistente...")
                
                # Wait for the run to complete
                while True:
                    run_status = client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    if run_status.status == 'completed':
                        break
                    elif run_status.status == 'failed':
                        raise Exception("Run failed")
                
                # Get the assistant's response
                messages = client.beta.threads.messages.list(
                    thread_id=thread.id,
                    order='desc',
                    limit=1
                )
                
                # Store the complete response
                if messages.data:
                    response = messages.data[0].content[0].text.value
                    results.append({
                        "Sección": section,
                        "Pregunta": question,
                        "Respuesta": response
                    })
                    print("✓ Respuesta recibida")
                else:
                    print("⚠ No se recibió respuesta")
        
        return results
    except Exception as e:
        print(f"\n❌ Error al procesar las preguntas")
        print(f"Error: {str(e)}")
        return None

def main():
    # Create output directory if it doesn't exist
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    
    # Get all answers using the assistant
    results = analyze_with_assistant()
    
    if results is None:
        print("\n❌ No se pudieron obtener resultados")
        return
    
    # Create DataFrame and save to Excel with timestamp
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"analisis_resultados_{timestamp}.xlsx"
    
    try:
        df.to_excel(output_file, index=False)
        print(f"\n✓ Resultados guardados en: {output_file}")
    except PermissionError:
        print("\n❌ Error: No se puede guardar el archivo. Por favor, cierra el archivo Excel si está abierto.")
        # Intentar con un nombre alternativo
        alt_output_file = output_dir / f"analisis_resultados_{timestamp}_nuevo.xlsx"
        try:
            df.to_excel(alt_output_file, index=False)
            print(f"\n✓ Resultados guardados en: {alt_output_file}")
        except PermissionError:
            print("\n❌ Error: No se puede guardar el archivo. Por favor, verifica los permisos de la carpeta output/")

if __name__ == "__main__":
    main() 