# Análisis de Planes de Seguridad y Convivencia Ciudadana

Este proyecto automatiza el análisis de documentos de planes de seguridad y convivencia ciudadana utilizando OpenAI GPT-4.

## Estructura del Proyecto

```
.
├── data/
│   └── raw/           # Documentos a analizar
├── output/            # Resultados del análisis
├── src/              # Código fuente
│   ├── analyze_document.py
│   └── config.py
├── .env              # Configuración de OpenAI
├── requirements.txt  # Dependencias del proyecto
└── README.md         # Este archivo
```

## Configuración

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Crear un archivo `.env` en la raíz del proyecto con la siguiente variable:
```
OPENAI_API_KEY="tu-api-key"
```

La variable requerida es:
- `OPENAI_API_KEY`: Tu clave de API de OpenAI

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