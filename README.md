# RAG Multimodal PoC

Prueba de concepto de un sistema RAG multimodal que procesa documentos PDF con texto, tablas e imágenes.

## Arquitectura

**Modelos:**
- **LLM Local:** Qwen 2.5 8B (via Ollama) - Generación de respuestas
- **Embeddings Local:** bge-m3 (via Ollama) - Vectorización de texto
- **Vision Multimodal:** nvidia/nemotron-nano-12b-v2-vl (via OpenRouter) - Análisis de imágenes

**Procesamiento:**
- **Parser:** MinerU - Extracción de contenido de PDFs
- **Backend RAG:** LightRAG - Base de datos vectorial y knowledge graph

## Estructura del Proyecto

```
rag-multimodal-poc/
├── config/
│   └── config.yaml              # Configuración de modelos
├── data/
│   ├── input/                   # Colocar PDFs aquí
│   └── processed/               # Output temporal de MinerU
├── storage/
│   └── rag_storage/             # Base de datos vectorial (generada)
├── src/
│   ├── models.py                # Wrappers para modelos
│   └── utils.py                 # Utilidades
├── 1_index_documents.py         # FASE 1: Indexar documentos
├── 2_query_rag.py               # FASE 2: Realizar queries
├── requirements.txt
└── .env                         # API keys
```

## Instalación

### 1. Prerequisitos

**Ollama instalado y ejecutando:**
```bash
# Verificar que Ollama esté corriendo
ollama --version

# Descargar modelos necesarios
ollama pull qwen2.5:8b
ollama pull bge-m3
```

**Python 3.10+**

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar API Key

Editar `.env` y agregar tu OpenRouter API key:
```
OPENROUTER_API_KEY=tu_api_key_real
```

## Uso

### FASE 1: Indexar Documentos

1. Colocar archivos PDF en `data/input/`

2. Ejecutar indexación:
```bash
python 1_index_documents.py
```

Este proceso:
- Extrae texto, tablas e imágenes de los PDFs con MinerU
- Genera embeddings con bge-m3
- Analiza imágenes con nvidia/nemotron
- Crea knowledge graph con Qwen 8B
- Almacena todo en `storage/rag_storage/`

### FASE 2: Realizar Queries

Una vez indexados los documentos:

```bash
python 2_query_rag.py "¿Qué dice sobre el tema X?"
python 2_query_rag.py "Resume la tabla de resultados del capítulo 2"
python 2_query_rag.py "Explica el diagrama de la página 5"
```

**Flujo de Query:**
1. Query de texto del usuario
2. Búsqueda vectorial con bge-m3
3. Recuperación de contexto (texto + tablas + imágenes)
4. Si hay imágenes → nvidia/nemotron las analiza
5. Qwen 8B genera respuesta final

## Configuración

Editar `config/config.yaml` para ajustar:

```yaml
ollama:
  llm_model: "qwen2.5:8b"          # Cambiar modelo LLM
  embedding_model: "bge-m3"         # Cambiar modelo embeddings

openrouter:
  vision_model: "nvidia/nemotron-nano-12b-v2-vl"  # Cambiar modelo vision

mineru:
  parse_method: "auto"              # Opciones: auto, ocr, txt
  device: "cpu"                     # Cambiar a "cuda" si tienes GPU
```

## Notas

- La indexación solo se hace una vez (o cuando agregues nuevos documentos)
- Las queries pueden ejecutarse múltiples veces sin re-indexar
- Para agregar más documentos: colocar PDFs en `data/input/` y ejecutar `1_index_documents.py` nuevamente
- MinerU descargará modelos automáticamente en la primera ejecución

## Troubleshooting

**Error: "Ollama connection refused"**
- Verificar que Ollama esté ejecutándose: `ollama serve`

**Error: "Model not found"**
- Descargar el modelo: `ollama pull nombre_modelo`

**Error: "OPENROUTER_API_KEY not found"**
- Verificar que `.env` exista y contenga la API key

**Procesamiento muy lento**
- Cambiar `device: "cuda"` en `config.yaml` si tienes GPU
- Reducir número de documentos para prueba inicial
