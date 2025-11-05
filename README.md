# PoC RAG-Anything + HuggingFace (Local)
Sistema RAG multimodal usando modelos locales de HuggingFace para documentos PDF en español.

## Arquitectura

```
PDF → MinerU → Texto/Imágenes/Tablas → RAGAnything → Knowledge Graph
                                            ↓
                            Qwen-8B + QwenVL + bge-m3
                                            ↓
                                    Query en español
```

## Estructura del proyecto

```
poc-rag/
├── config.py              # Configuración central
├── 1_setup.sh             # Instalación de dependencias
├── 2_parse_pdf.py         # Parsing con MinerU
├── 3_load_models.py       # Carga de modelos locales
├── 4_wrappers.py          # Adaptadores para RAGAnything
├── 5_process_document.py  # Procesamiento del documento
└── 6_query.py             # Sistema de queries
```

## Uso

### 1. Setup inicial

```bash
chmod +x 1_setup.sh
./1_setup.sh
```

### 2. Configurar tu PDF

Edita `config.py` y cambia:
```python
PDF_PATH = "ruta/a/tu/documento.pdf"
```

### 3. Opción A: Pipeline completo (recomendado)

```bash
# Procesar documento (incluye parsing + construcción del knowledge graph)
python 5_process_document.py

# Hacer queries
python 6_query.py --interactive
```

### 4. Opción B: Paso a paso

```bash
# Paso 1: Parsear PDF con MinerU
python 2_parse_pdf.py

# Paso 2: Test de modelos
python 3_load_models.py

# Paso 3: Test de wrappers
python 4_wrappers.py

# Paso 4: Procesar documento
python 5_process_document.py

# Paso 5: Queries
python 6_query.py --interactive
```

## Modos de query

- **hybrid**: Combina vector search + graph traversal (recomendado)
- **local**: Búsqueda local en el grafo
- **global**: Búsqueda global
- **naive**: Vector search básico

Cambiar modo en interactivo:
```
[hybrid] Pregunta: modo local
```

## Ejemplos de queries

```
¿Cuál es el tema principal del documento?
Resume el contenido de las tablas
¿Qué información aparece en las imágenes?
Explica los conceptos clave del documento
```

## Gestión de memoria GPU (24GB VRAM)

### Durante procesamiento:
- Qwen-8B (4-bit): ~5GB
- QwenVL (4-bit): ~3GB
- bge-m3: ~2GB
- MinerU: ~2GB
- Working: ~12GB libre

### Durante queries:
- Qwen-8B (4-bit): ~5GB
- bge-m3: ~2GB
- Working: ~17GB libre

El script descarga automáticamente el Vision Model después del procesamiento.

## Troubleshooting

### Error: CUDA out of memory
- Reducir batch size en embeddings
- Usar modelos más pequeños
- Procesar menos imágenes simultáneamente

### Error: MinerU no encontrado
```bash
pip install magic-pdf --break-system-packages
mineru --version
```

### Error: Knowledge graph no encontrado
Ejecuta primero `5_process_document.py`

## Personalización

### Cambiar modelos

Edita `config.py`:
```python
LLM_MODEL = "tu/modelo"
VISION_MODEL = "tu/vision-model"
EMBEDDING_MODEL = "tu/embedding-model"
```

### Cambiar configuración MinerU

Edita `config.py`:
```python
MINERU_PARSE_METHOD = "ocr"  # auto, ocr, txt
MINERU_LANG = "es"
```

### Deshabilitar procesamiento de imágenes/tablas

Edita `config.py`:
```python
ENABLE_IMAGE_PROCESSING = False
ENABLE_TABLE_PROCESSING = False
```

## Notas

- Primera ejecución descarga modelos (puede tardar)
- bge-m3 soporta español nativamente
- Los embeddings se guardan en `rag_storage/`
- El knowledge graph es reutilizable
