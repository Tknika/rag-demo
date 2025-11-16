# Documentación Técnica - RAG Multimodal PoC

## Resumen de Arquitectura

### Stack Tecnológico

**Capa de Modelos:**
- **LLM:** Qwen 2.5 8B (Ollama) - Generación de texto y construcción de knowledge graph
- **Embeddings:** bge-m3 (Ollama) - 1024 dimensiones, búsqueda semántica
- **Vision:** nvidia/nemotron-nano-12b-v2-vl (OpenRouter) - Análisis multimodal

**Capa de Procesamiento:**
- **Parser:** MinerU - Extracción estructurada de PDFs
- **Framework:** RAG-Anything - Orquestación multimodal
- **Backend:** LightRAG - Knowledge graph + vector DB

## Flujo de Datos

### FASE 1: Indexación

```
PDF Input
    ↓
MinerU Parser
    ↓
┌─────────────┬─────────────┬─────────────┐
│   Texto     │   Tablas    │  Imágenes   │
└─────────────┴─────────────┴─────────────┘
    ↓              ↓              ↓
bge-m3        bge-m3      nemotron-vl
(embeddings)  (embeddings)  (descripción)
    ↓              ↓              ↓
    └──────────────┴──────────────┘
                   ↓
            Qwen 8B (entities)
                   ↓
         LightRAG Knowledge Graph
                   ↓
          storage/rag_storage/
```

### FASE 2: Query

```
Query Texto Usuario
        ↓
bge-m3 (embedding)
        ↓
LightRAG Vector Search
        ↓
Contexto Recuperado
┌─────────┬─────────┬─────────┐
│ Texto   │ Tablas  │ Imágenes│
└─────────┴─────────┴─────────┘
     ↓         ↓         ↓
     │         │    nemotron-vl
     │         │    (analiza)
     │         │         ↓
     └─────────┴─────────┘
              ↓
        Qwen 8B (síntesis)
              ↓
     Respuesta Final
```

## Decisiones de Diseño

### 1. Separación en 2 Fases

**Razón:** 
- Indexación es costosa (una vez o al agregar docs)
- Queries son rápidas (múltiples veces)
- Facilita testing y debugging

### 2. Modelo Local vs Cloud

**Local (Ollama):**
- LLM y Embeddings: Privacidad, sin costos API
- Latencia controlada en entorno local

**Cloud (OpenRouter):**
- Vision: Calidad superior para análisis multimodal
- Uso esporádico (solo cuando hay imágenes)

### 3. bge-m3 como Embedding

**Ventajas:**
- 1024 dims (balance capacidad/velocidad)
- Multilingüe (español/inglés)
- Open source, ejecutable en Ollama

### 4. MinerU como Parser

**Ventajas:**
- Preserva estructura de documento
- Extrae tablas con precisión
- Manejo robusto de layouts complejos

### 5. LightRAG como Backend

**Ventajas:**
- Knowledge graph automático
- Búsqueda híbrida (vector + graph)
- Integración nativa con RAG-Anything

## Estructura de Código

### src/models.py

**Responsabilidades:**
- Wrappers para conexión con modelos
- Manejo de formatos específicos (Ollama API, OpenRouter API)
- Encapsulación de lógica de comunicación

**Funciones clave:**
```python
create_ollama_llm_func()      # Wrapper para Qwen
create_ollama_embed_func()    # Wrapper para bge-m3
create_openrouter_vision_func()  # Wrapper para nemotron
```

### src/utils.py

**Responsabilidades:**
- Carga de configuración YAML
- Escaneo de archivos PDF
- Creación de directorios

### 1_index_documents.py

**Flujo:**
1. Cargar configuración
2. Inicializar modelos (LLM, Embed, Vision)
3. Crear instancia RAGAnything
4. Iterar sobre PDFs en data/input/
5. Procesar cada documento
6. Persistir en storage/

**Nota:** RAGAnything llama internamente a MinerU

### 2_query_rag.py

**Flujo:**
1. Verificar que existe storage/
2. Cargar configuración
3. Inicializar modelos
4. Cargar RAG desde storage existente
5. Ejecutar query (modo hybrid)
6. Mostrar resultado

## Configuración

### config.yaml

**Secciones:**

**ollama:** URLs y nombres de modelos locales
**openrouter:** API y modelo vision
**paths:** Rutas de directorios
**mineru:** Parámetros de parsing (auto/ocr/txt, cpu/cuda)
**rag:** Flags de procesamiento (image/table/equation)

### .env

Variables sensibles:
- OPENROUTER_API_KEY

## Optimizaciones Posibles

### Para Producción:

1. **Batch Processing:**
   - Procesar múltiples PDFs en paralelo
   - Usar asyncio para I/O concurrente

2. **Cache:**
   - Cache de embeddings repetidos
   - Cache de análisis de imágenes similares

3. **Streaming:**
   - Respuestas en stream para mejor UX
   - Feedback de progreso durante indexación

4. **Monitoreo:**
   - Logging estructurado
   - Métricas de latencia
   - Conteo de tokens (costos)

### Para Escalabilidad:

1. **Vector DB Externo:**
   - Qdrant/Weaviate/Pinecone
   - Búsqueda distribuida

2. **GPU Acceleration:**
   - CUDA para MinerU
   - vLLM para Qwen

3. **Modelo Vision Local:**
   - LLaVA/Qwen-VL local
   - Eliminar dependencia OpenRouter

## Testing

### Test Manual:

```bash
# 1. Indexar documento de prueba
cp test.pdf data/input/
python 1_index_documents.py

# 2. Queries de prueba
python 2_query_rag.py "Resume el documento"
python 2_query_rag.py "¿Qué muestra la tabla?"
python 2_query_rag.py "Explica el diagrama"
```

### Validaciones:

- Verificar que storage/ contiene archivos
- Comprobar dimensiones de embeddings (1024)
- Validar formato de respuestas
- Testing con PDFs de diferentes tipos

## Limitaciones Actuales

1. **Ecuaciones:** Deshabilitadas (enable_equation_processing=false)
2. **Formatos:** Solo PDF (no DOC/PPTX)
3. **Lenguaje:** Configurado para auto-detect (español/inglés)
4. **Concurrencia:** Procesamiento secuencial
5. **Error Handling:** Básico, mejorable

## Extensiones Futuras

1. Soporte para más formatos (DOC, PPTX, Excel)
2. UI web (Streamlit/Gradio)
3. API REST para integración
4. Fine-tuning de modelos con feedback
5. Procesamiento de ecuaciones LaTeX
6. Multilenguaje avanzado
