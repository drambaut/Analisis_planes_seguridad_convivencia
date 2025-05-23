# Análisis de Planes de Seguridad y Convivencia Ciudadana

Este proyecto automatiza el análisis de documentos de planes de seguridad y convivencia ciudadana utilizando Azure OpenAI (ChatGPT).

## Estructura del Proyecto

```
.
├── data/
│   └── raw/           # Documentos a analizar
├── output/            # Resultados del análisis
├── src/              # Código fuente
│   ├── analyze_document.py
│   └── config.py
├── .env              # Configuración de Azure OpenAI
├── requirements.txt  # Dependencias del proyecto
└── README.md         # Este archivo
```

## Configuración

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
```
AZURE_OPENAI_API_KEY="tu-api-key"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"
AZURE_OPENAI_ENDPOINT="tu-endpoint"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-35-turbo"
```

Las variables requeridas son:
- `AZURE_OPENAI_API_KEY`: Tu clave de API de Azure OpenAI
- `AZURE_OPENAI_ENDPOINT`: El endpoint de tu instancia de Azure OpenAI

Las variables opcionales son:
- `AZURE_OPENAI_API_VERSION`: Versión de la API (por defecto: "2024-12-01-preview")
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Nombre del despliegue (por defecto: "gpt-35-turbo")

## Uso

1. Colocar los documentos a analizar en la carpeta `data/raw/`
2. Ejecutar el script:
```bash
python src/analyze_document.py
```

Los resultados se guardarán en la carpeta `output/` en formato Excel.

## Características

- Análisis automático de documentos
- Extracción de información estructurada
- Respuestas basadas en preguntas predefinidas
- Exportación a Excel
- Manejo de errores y casos sin respuesta
- Configuración segura mediante variables de entorno