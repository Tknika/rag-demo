# 🎓 Workshop: RAG Multimodal con LightRAG

## 📋 Índice

1. [Arquitectura General](#arquitectura-general)
2. [Fase 1: Indexación de Documentos](#fase-1-indexación-de-documentos)
3. [Fase 2: Query y Retrieval](#fase-2-query-y-retrieval)
4. [Modelos Utilizados](#modelos-utilizados)
5. [Bases de Datos](#bases-de-datos)
6. [Flujo Completo End-to-End](#flujo-completo-end-to-end)

---

## Arquitectura General

```mermaid
graph TB
    subgraph "Input"
        PDF[📄 PDF Document]
    end
    
    subgraph "Fase 1: Indexación"
        MINERU[MinerU Parser]
        SPLIT[Content Splitter]
        TEXT[📝 Text Chunks]
        IMG[🖼️ Images]
        TBL[📊 Tables]
    end
    
    subgraph "Modelos"
        LLM[🤖 Qwen3 14B<br/>Entity Extraction]
        EMBED[🔢 BGE-M3<br/>Embeddings]
        VISION[👁️ Nemotron-VL<br/>Vision Analysis]
    end
    
    subgraph "Fase 2: Storage"
        GRAPH[📊 Knowledge Graph<br/>NetworkX]
        VECTOR[🗄️ Vector DB<br/>Nano Vector DB]
        KV[💾 Key-Value Store<br/>JSON Files]
    end
    
    subgraph "Query"
        USER[👤 User Query]
        RETRIEVAL[🔍 Hybrid Search]
        RESPONSE[💬 Final Answer]
    end
    
    PDF --> MINERU
    MINERU --> SPLIT
    SPLIT --> TEXT
    SPLIT --> IMG
    SPLIT --> TBL
    
    TEXT --> EMBED
    TEXT --> LLM
    IMG --> VISION
    TBL --> VISION
    
    LLM --> GRAPH
    EMBED --> VECTOR
    VISION --> KV
    
    USER --> RETRIEVAL
    RETRIEVAL --> VECTOR
    RETRIEVAL --> GRAPH
    RETRIEVAL --> KV
    VECTOR --> LLM
    GRAPH --> LLM
    KV --> LLM
    LLM --> RESPONSE
```

---

## Fase 1: Indexación de Documentos

### 1.1 Flujo Completo de Indexación

```mermaid
flowchart TD
    START([🚀 Inicio: python 1_index_documents.py])
    
    START --> LOAD_CONFIG[📋 Cargar config.yaml + .env]
    LOAD_CONFIG --> INIT_MODELS[🔧 Inicializar Modelos]
    
    subgraph MODELS [" 🤖 Modelos "]
        LLM_INIT[Qwen3 14B - Ollama<br/>localhost:11434]
        EMBED_INIT[BGE-M3 - Ollama<br/>localhost:11434]
        VISION_INIT[Nemotron-VL - OpenRouter<br/>API remota]
    end
    
    INIT_MODELS --> LLM_INIT
    INIT_MODELS --> EMBED_INIT
    INIT_MODELS --> VISION_INIT
    
    LLM_INIT --> SCAN_FILES
    EMBED_INIT --> SCAN_FILES
    VISION_INIT --> SCAN_FILES
    
    SCAN_FILES[📂 Escanear data/input/*.pdf]
    SCAN_FILES --> LOOP_START{Más PDFs?}
    
    LOOP_START -->|Sí| PARSE[🔍 MinerU Parse PDF]
    LOOP_START -->|No| END_INDEX([✅ Fin Indexación])
    
    PARSE --> SEPARATE[🔀 Separar Contenido]
    
    subgraph CONTENT [" 📦 Tipos de Contenido "]
        TEXT_CONTENT[📝 Texto<br/>12,991 chars]
        IMAGE_CONTENT[🖼️ Imágenes x4]
        TABLE_CONTENT[📊 Tablas x1]
        DISCARDED[🗑️ Descartado x8]
    end
    
    SEPARATE --> TEXT_CONTENT
    SEPARATE --> IMAGE_CONTENT
    SEPARATE --> TABLE_CONTENT
    SEPARATE --> DISCARDED
    
    TEXT_CONTENT --> PROCESS_TEXT
    IMAGE_CONTENT --> PROCESS_MODAL
    TABLE_CONTENT --> PROCESS_MODAL
    
    PROCESS_TEXT[⚙️ Procesar Texto]
    PROCESS_MODAL[⚙️ Procesar Multimodal]
    
    PROCESS_TEXT --> TEXT_COMPLETE
    PROCESS_MODAL --> MODAL_COMPLETE
    
    TEXT_COMPLETE --> LOOP_START
    MODAL_COMPLETE --> LOOP_START
    
    style MODELS fill:#E3F2FD
    style CONTENT fill:#FFF3E0
```

### 1.2 Procesamiento de Texto (Detallado)

```mermaid
flowchart TD
    TEXT_IN[📝 Texto Completo<br/>12,991 caracteres]
    
    TEXT_IN --> CHUNK[✂️ Chunking Inteligente]
    
    subgraph CHUNKING [" ✂️ Estrategia de Chunking "]
        SEMANTIC[Semantic Chunking<br/>Basado en párrafos/secciones]
        SIZE[Chunk Size: ~1200 tokens<br/>Overlap: 200 tokens]
        RESULT[Resultado: 13 chunks]
    end
    
    CHUNK --> SEMANTIC
    SEMANTIC --> SIZE
    SIZE --> RESULT
    
    RESULT --> PARALLEL{Procesamiento Paralelo}
    
    subgraph EMBEDDING [" 🔢 Embedding Pipeline "]
        EMB1[📊 BGE-M3 Embedding]
        EMB2[Vector 1024-dim]
        EMB3[💾 Guardar en Vector DB]
    end
    
    subgraph ENTITY [" 🤖 Entity Extraction "]
        LLM1[Qwen3 14B]
        LLM2[🏷️ Extract Entities<br/>🔗 Extract Relations]
        LLM3[Formato estructurado]
        LLM4[Entity~Relation~Description~Weight]
    end
    
    PARALLEL --> EMBEDDING
    PARALLEL --> ENTITY
    
    EMB1 --> EMB2
    EMB2 --> EMB3
    
    LLM1 --> LLM2
    LLM2 --> LLM3
    LLM3 --> LLM4
    
    EMB3 --> BUILD_GRAPH
    LLM4 --> BUILD_GRAPH
    
    BUILD_GRAPH[🕸️ Construir Knowledge Graph]
    
    subgraph GRAPH_BUILD [" 📊 Knowledge Graph "]
        NODES[Crear Nodos<br/>169 entidades]
        EDGES[Crear Edges<br/>313 relaciones]
        TYPES[Tipos: person, artifact,<br/>method, event, organization]
    end
    
    BUILD_GRAPH --> NODES
    NODES --> EDGES
    EDGES --> TYPES
    
    TYPES --> SAVE_GRAPH[💾 Persistir Graph<br/>graph_chunk_entity_relation.graphml]
    SAVE_GRAPH --> SAVE_VECTOR[💾 Persistir Vectors<br/>vdb_entities.json]
    SAVE_VECTOR --> SAVE_KV[💾 Persistir KV<br/>kv_store_*.json]
    
    SAVE_KV --> TEXT_DONE([✅ Texto Procesado])
    
    style CHUNKING fill:#E8EAF6
    style EMBEDDING fill:#F3E5F5
    style ENTITY fill:#E0F2F1
    style GRAPH_BUILD fill:#FFF9C4
```

### 1.3 Procesamiento Multimodal (Detallado)

```mermaid
flowchart TD
    MODAL_IN[🎨 Contenido Multimodal<br/>14 items]
    
    MODAL_IN --> CLASSIFY{Clasificar Tipo}
    
    CLASSIFY -->|4 items| IMG_PROC[🖼️ Imágenes]
    CLASSIFY -->|1 item| TBL_PROC[📊 Tablas]
    CLASSIFY -->|8 items| DISC_PROC[🗑️ Descartado]
    CLASSIFY -->|1 item| EQ_PROC[🔢 Ecuaciones]
    
    subgraph IMAGE_PIPELINE [" 🖼️ Pipeline de Imágenes "]
        IMG1[Extraer contexto de página]
        IMG2[Texto antes/después de imagen]
        IMG3[Capítulo/sección actual]
        IMG4[👁️ Nemotron-VL Vision Model]
        IMG5[Prompt: Describe imagen<br/>en contexto del documento]
        IMG6[📝 Descripción textual generada]
    end
    
    subgraph TABLE_PIPELINE [" 📊 Pipeline de Tablas "]
        TBL1[Extraer estructura de tabla]
        TBL2[Detectar headers/filas]
        TBL3[Contexto de sección]
        TBL4[👁️ Nemotron-VL Vision Model]
        TBL5[Prompt: Analizar datos<br/>y relaciones en tabla]
        TBL6[📝 Resumen estructurado]
    end
    
    IMG_PROC --> IMG1
    IMG1 --> IMG2
    IMG2 --> IMG3
    IMG3 --> IMG4
    IMG4 --> IMG5
    IMG5 --> IMG6
    
    TBL_PROC --> TBL1
    TBL1 --> TBL2
    TBL2 --> TBL3
    TBL3 --> TBL4
    TBL4 --> TBL5
    TBL5 --> TBL6
    
    IMG6 --> EMBED_MODAL
    TBL6 --> EMBED_MODAL
    DISC_PROC --> SKIP[❌ Skip Processing]
    EQ_PROC --> SKIP
    
    EMBED_MODAL[🔢 BGE-M3 Embedding<br/>de descripción textual]
    
    EMBED_MODAL --> ENTITY_EXTRACT[🤖 Qwen3 14B<br/>Extraer entidades de descripción]
    
    ENTITY_EXTRACT --> CREATE_CHUNK[📦 Crear Chunk Multimodal]
    
    subgraph CHUNK_STRUCTURE [" 📦 Estructura del Chunk "]
        C1[ID único]
        C2[Tipo: image/table]
        C3[Descripción textual]
        C4[Vector embedding]
        C5[Entidades extraídas]
        C6[Relaciones con texto]
        C7[Metadatos: página, posición]
    end
    
    CREATE_CHUNK --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5
    C5 --> C6
    C6 --> C7
    
    C7 --> SAVE_MODAL[💾 Guardar en Storage]
    SKIP --> SAVE_MODAL
    
    subgraph STORAGE [" 💾 Storage Multimodal "]
        S1[Vector DB: embeddings]
        S2[Knowledge Graph: entidades]
        S3[KV Store: metadata + descripciones]
    end
    
    SAVE_MODAL --> S1
    SAVE_MODAL --> S2
    SAVE_MODAL --> S3
    
    S3 --> MODAL_DONE([✅ Multimodal Procesado])
    
    style IMAGE_PIPELINE fill:#E3F2FD
    style TABLE_PIPELINE fill:#F3E5F5
    style CHUNK_STRUCTURE fill:#FFF3E0
    style STORAGE fill:#E8F5E9
```

---

## Fase 2: Query y Retrieval

### 2.1 Flujo Completo de Query

```mermaid
flowchart TD
    START([🚀 Inicio: python 2_query_rag.py])
    
    START --> INPUT[👤 Usuario ingresa query<br/>¿Qué es DeepSeek-OCR?]
    
    INPUT --> LOAD_SYSTEM[🔧 Cargar Sistema]
    
    subgraph LOAD [" 🔧 Carga del Sistema "]
        L1[Cargar modelos LLM + Embed + Vision]
        L2[Conectar a LightRAG storage]
        L3[Cargar Knowledge Graph<br/>199 nodos, 364 edges]
        L4[Cargar Vector DB]
        L5[Cargar KV Store]
    end
    
    LOAD_SYSTEM --> L1
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5
    
    L5 --> EMBED_QUERY[🔢 BGE-M3: Embedizar Query<br/>Vector 1024-dim]
    
    EMBED_QUERY --> HYBRID_SEARCH{🔍 Hybrid Search}
    
    subgraph RETRIEVAL [" 🔍 Estrategia de Retrieval "]
        R1[1️⃣ Local Search<br/>Vector similarity]
        R2[2️⃣ Global Search<br/>Knowledge graph traversal]
        R3[3️⃣ Naive Search<br/>Keyword matching]
    end
    
    HYBRID_SEARCH --> R1
    HYBRID_SEARCH --> R2
    HYBRID_SEARCH --> R3
    
    R1 --> LOCAL_DETAILS
    R2 --> GLOBAL_DETAILS
    R3 --> NAIVE_DETAILS
    
    subgraph LOCAL_DETAILS [" 1️⃣ Local Search (Vector) "]
        LOC1[Buscar en Vector DB]
        LOC2[Top-K=20 chunks similares]
        LOC3[Cosine similarity > 0.7]
        LOC4[📝 Chunks de texto<br/>🖼️ Chunks de imágenes<br/>📊 Chunks de tablas]
    end
    
    subgraph GLOBAL_DETAILS [" 2️⃣ Global Search (Graph) "]
        GLO1[Buscar entidades en grafo]
        GLO2[Encontrar: DeepSeek-OCR node]
        GLO3[Explorar relaciones<br/>1-hop: 15 conexiones<br/>2-hop: 45 conexiones]
        GLO4[Obtener contexto de vecinos]
    end
    
    subgraph NAIVE_DETAILS [" 3️⃣ Naive Search (Keywords) "]
        NAI1[Tokenizar query]
        NAI2[Buscar keywords en KV]
        NAI3[Matching exacto de términos]
        NAI4[Fallback si otros fallan]
    end
    
    LOC1 --> LOC2
    LOC2 --> LOC3
    LOC3 --> LOC4
    
    GLO1 --> GLO2
    GLO2 --> GLO3
    GLO3 --> GLO4
    
    NAI1 --> NAI2
    NAI2 --> NAI3
    NAI3 --> NAI4
    
    LOC4 --> MERGE
    GLO4 --> MERGE
    NAI4 --> MERGE
    
    MERGE[🔗 Merge & Rank Results]
    
    subgraph RANKING [" 📊 Ranking Strategy "]
        RNK1[Eliminar duplicados]
        RNK2[Score ponderado:<br/>Vector: 40%<br/>Graph: 40%<br/>Keyword: 20%]
        RNK3[Re-rank por relevancia]
        RNK4[Top-10 chunks finales]
    end
    
    MERGE --> RNK1
    RNK1 --> RNK2
    RNK2 --> RNK3
    RNK3 --> RNK4
    
    RNK4 --> BUILD_CONTEXT
    
    BUILD_CONTEXT[📝 Construir Contexto]
    
    subgraph CONTEXT [" 📝 Context Building "]
        CTX1[Chunk 1: Texto principal]
        CTX2[Chunk 2: Descripción de imagen]
        CTX3[Chunk 3: Datos de tabla]
        CTX4[Chunk 4-10: Contexto adicional]
        CTX5[Entidades relacionadas del grafo]
        CTX6[Total: ~4000 tokens]
    end
    
    BUILD_CONTEXT --> CTX1
    CTX1 --> CTX2
    CTX2 --> CTX3
    CTX3 --> CTX4
    CTX4 --> CTX5
    CTX5 --> CTX6
    
    CTX6 --> GENERATE
    
    GENERATE[🤖 Qwen3 14B: Generar Respuesta]
    
    subgraph GENERATION [" 🤖 Response Generation "]
        GEN1[System Prompt:<br/>Eres un asistente experto...]
        GEN2[User Query + Contexto]
        GEN3[Temperature: 0.1<br/>Max tokens: 2048]
        GEN4[Streaming response]
    end
    
    GENERATE --> GEN1
    GEN1 --> GEN2
    GEN2 --> GEN3
    GEN3 --> GEN4
    
    GEN4 --> OUTPUT[💬 Respuesta Final al Usuario]
    
    OUTPUT --> LOG[📊 Log Metrics]
    
    subgraph METRICS [" 📊 Métricas "]
        M1[Tiempo total: ~12s]
        M2[Chunks recuperados: 10]
        M3[Tokens usados: 4521]
        M4[Modelo LLM: Qwen3 14B]
        M5[Fuentes: texto + imagen + tabla]
    end
    
    LOG --> M1
    M1 --> M2
    M2 --> M3
    M3 --> M4
    M4 --> M5
    
    M5 --> END([✅ Fin Query])
    
    style LOAD fill:#E3F2FD
    style RETRIEVAL fill:#FFF3E0
    style LOCAL_DETAILS fill:#E8F5E9
    style GLOBAL_DETAILS fill:#F3E5F5
    style NAIVE_DETAILS fill:#FFF9C4
    style RANKING fill:#FCE4EC
    style CONTEXT fill:#E0F2F1
    style GENERATION fill:#F1F8E9
    style METRICS fill:#EFEBE9
```

### 2.2 Detalle de Hybrid Search

```mermaid
graph TB
    QUERY[Query: ¿Qué es DeepSeek-OCR?]
    
    subgraph VECTOR_SEARCH [" 🔢 Vector Search "]
        V1[Embedizar query con BGE-M3]
        V2[Buscar en vector_db_entities.json]
        V3[Calcular cosine similarity]
        V4[Top-20 chunks por similitud]
        V5[Score: 0.85 - 0.72]
    end
    
    subgraph GRAPH_SEARCH [" 🕸️ Graph Search "]
        G1[Buscar en grafo NetworkX]
        G2[Encontrar nodo: DeepSeek-OCR]
        G3[Explorar vecinos 1-hop]
        G4[Relaciones: uses, part-of,<br/>evaluated-on, compared-with]
        G5[15 nodos conectados]
    end
    
    subgraph NAIVE_SEARCH [" 🔤 Keyword Search "]
        N1[Tokenizar: deepseek, ocr]
        N2[Buscar en full_docs.json]
        N3[Matching de strings]
        N4[8 documentos matcheados]
    end
    
    QUERY --> V1
    QUERY --> G1
    QUERY --> N1
    
    V1 --> V2
    V2 --> V3
    V3 --> V4
    V4 --> V5
    
    G1 --> G2
    G2 --> G3
    G3 --> G4
    G4 --> G5
    
    N1 --> N2
    N2 --> N3
    N3 --> N4
    
    V5 --> MERGE[⚖️ Merge & Deduplicate]
    G5 --> MERGE
    N4 --> MERGE
    
    MERGE --> RERANK[📊 Re-rank by Combined Score]
    
    RERANK --> FINAL[✅ Top-10 Final Results]
    
    style VECTOR_SEARCH fill:#E3F2FD
    style GRAPH_SEARCH fill:#F3E5F5
    style NAIVE_SEARCH fill:#FFF3E0
```

---

## Modelos Utilizados

### Tabla Comparativa

| Modelo | Uso | Proveedor | Dimensión | Velocidad | Cuándo se Usa |
|--------|-----|-----------|-----------|-----------|---------------|
| **Qwen3 14B** | LLM para extracción de entidades y generación de respuestas | Ollama (local) | - | ~2s/chunk | Fase 1: Extracción de entidades<br/>Fase 2: Generación de respuesta |
| **BGE-M3** | Embeddings de texto | Ollama (local) | 1024-dim | ~100ms/texto | Fase 1: Vectorizar chunks<br/>Fase 2: Vectorizar query |
| **Nemotron-VL** | Análisis de imágenes y tablas | OpenRouter (API) | - | ~3-5s/imagen | Fase 1: Describir imágenes/tablas |

### Flujo de Llamadas a Modelos

```mermaid
sequenceDiagram
    participant U as User
    participant S as Sistema
    participant O as Ollama Local
    participant R as OpenRouter API
    
    Note over U,R: FASE 1: INDEXACIÓN
    
    U->>S: Ejecutar 1_index_documents.py
    S->>O: 13 llamadas a BGE-M3 (embeddings de chunks)
    O-->>S: 13 vectores [1024-dim]
    
    S->>O: 13 llamadas a Qwen3 14B (extraer entidades)
    O-->>S: 169 entidades + 313 relaciones
    
    S->>R: 4 llamadas a Nemotron-VL (imágenes)
    R-->>S: 4 descripciones textuales
    
    S->>R: 1 llamada a Nemotron-VL (tabla)
    R-->>S: 1 descripción estructurada
    
    S->>O: 5 llamadas a BGE-M3 (embeddings multimodal)
    O-->>S: 5 vectores [1024-dim]
    
    S->>O: 5 llamadas a Qwen3 14B (entidades multimodal)
    O-->>S: 30 entidades + 51 relaciones adicionales
    
    Note over S: Total: 199 nodos, 364 edges en grafo
    Note over S: Storage guardado en ./storage/rag_storage/
    
    Note over U,R: FASE 2: QUERY
    
    U->>S: Ejecutar 2_query_rag.py con query
    S->>O: 1 llamada a BGE-M3 (embedizar query)
    O-->>S: Vector query [1024-dim]
    
    Note over S: Búsqueda en Vector DB (local)
    Note over S: Búsqueda en Knowledge Graph (local)
    Note over S: Hybrid merge de resultados
    
    S->>O: 1 llamada a Qwen3 14B (generar respuesta)
    Note over O: Context: 10 chunks (4000 tokens)
    O-->>S: Respuesta generada
    
    S-->>U: Respuesta final
    
    Note over U,R: Total llamadas Fase 2: 2 (BGE-M3 + Qwen3)
```

---

## Bases de Datos

### Estructura del Storage

```
storage/rag_storage/
├── graph_chunk_entity_relation.graphml   # Knowledge Graph (NetworkX)
│   └── 199 nodos, 364 edges
│
├── vdb_entities.json                     # Vector DB - Entidades
│   └── Embeddings de entidades extraídas
│
├── vdb_chunks.json                       # Vector DB - Chunks de texto
│   └── Embeddings de chunks originales
│
├── vdb_relationships.json                # Vector DB - Relaciones
│   └── Embeddings de descripciones de relaciones
│
├── kv_store_full_docs.json              # KV Store - Documentos completos
│   └── Metadata + texto completo por documento
│
├── kv_store_text_chunks.json            # KV Store - Chunks de texto
│   └── ID → contenido de chunk
│
├── kv_store_llm_response_cache.json     # Cache de respuestas LLM
│   └── Hash prompt → respuesta (evita recomputar)
│
└── doc_status.json                       # Estado de procesamiento
    └── Qué documentos están indexados
```

### Diagrama de Bases de Datos

```mermaid
graph LR
    subgraph VECTOR_DB [" 🗄️ Vector Database (Nano Vector DB) "]
        V1[vdb_entities.json<br/>169 vectores]
        V2[vdb_chunks.json<br/>13 vectores]
        V3[vdb_relationships.json<br/>313 vectores]
    end
    
    subgraph GRAPH_DB [" 🕸️ Knowledge Graph (NetworkX) "]
        G1[graph_chunk_entity_relation.graphml]
        G2[Nodos: 199<br/>person, artifact, method,<br/>event, organization]
        G3[Edges: 364<br/>uses, part-of, evaluated-on,<br/>compared-with, belongs-to]
    end
    
    subgraph KV_STORE [" 💾 Key-Value Store (JSON) "]
        K1[full_docs.json<br/>Documentos originales]
        K2[text_chunks.json<br/>Chunks indexados]
        K3[llm_response_cache.json<br/>Cache de LLM]
    end
    
    subgraph QUERY_ENGINE [" 🔍 Query Engine "]
        Q1[Hybrid Search]
        Q2[Vector Similarity]
        Q3[Graph Traversal]
        Q4[Keyword Match]
    end
    
    V1 --> Q2
    V2 --> Q2
    V3 --> Q2
    
    G1 --> Q3
    G2 --> Q3
    G3 --> Q3
    
    K1 --> Q4
    K2 --> Q4
    
    Q2 --> Q1
    Q3 --> Q1
    Q4 --> Q1
    
    Q1 --> RESULT[📝 Contexto<br/>para LLM]
    
    style VECTOR_DB fill:#E3F2FD
    style GRAPH_DB fill:#F3E5F5
    style KV_STORE fill:#FFF3E0
    style QUERY_ENGINE fill:#E8F5E9
```

### Ejemplo de Datos

#### Knowledge Graph Node (GraphML)
```xml
<node id="DeepSeek-OCR">
  <data key="d0">DeepSeek-OCR</data>
  <data key="d1">artifact</data>
  <data key="d2">DeepSeek-OCR is an optical compression method...</data>
  <data key="d3">chunk-7fe438c1c7cd83852645bb40d56fc405</data>
  <data key="d4">deepseek-ocr-paper_origin.pdf</data>
</node>
```

#### Vector DB Entry (JSON)
```json
{
  "DeepSeek-OCR": {
    "embedding": [0.023, -0.145, 0.892, ..., 0.234],  // 1024 dimensiones
    "metadata": {
      "type": "artifact",
      "source_chunk": "chunk-7fe438c1c...",
      "created_at": 1763128318
    }
  }
}
```

#### KV Store Entry (JSON)
```json
{
  "chunk-7fe438c1c7cd83852645bb40d56fc405": {
    "content": "DeepSeek-OCR: All-in-One Document Parsing...",
    "doc_id": "doc-393ccdd531c2dfc29c581ffbc9530c69",
    "file_path": "deepseek-ocr-paper_origin.pdf",
    "chunk_order": 1,
    "tokens": 487
  }
}
```

---

## Flujo Completo End-to-End

### Escenario Real: Pregunta sobre Imagen

```mermaid
sequenceDiagram
    participant U as 👤 Usuario
    participant P as 🔍 Parser (MinerU)
    participant V as 👁️ Vision Model
    participant E as 🔢 Embed Model
    participant L as 🤖 LLM
    participant G as 📊 Graph DB
    participant VDB as 🗄️ Vector DB
    participant K as 💾 KV Store
    
    Note over U,K: INDEXACIÓN DE IMAGEN
    
    U->>P: PDF con diagrama de arquitectura
    P->>P: Detectar imagen en página 3
    P->>P: Extraer contexto:<br/>Figure 2: DeepEncoder Architecture
    
    P->>V: 👁️ Nemotron-VL<br/>Imagen + contexto
    Note over V: Analiza imagen con IA
    V-->>P: The diagram shows a multi-layer<br/>architecture with SAM-base...
    
    P->>E: 🔢 BGE-M3<br/>Embedizar descripción
    E-->>P: Vector [1024-dim]
    
    P->>L: 🤖 Qwen3 14B<br/>Extraer entidades de descripción
    L-->>P: Entidades: [DeepEncoder, SAM-base,<br/>CLIP-large, Attention Layer]<br/>Relaciones: [uses, composed-of]
    
    P->>G: Guardar nodos y edges
    P->>VDB: Guardar embedding
    P->>K: Guardar metadata + descripción
    
    Note over U,K: QUERY SOBRE LA IMAGEN
    
    U->>L: Explica la arquitectura de DeepEncoder
    
    L->>E: 🔢 BGE-M3<br/>Embedizar query
    E-->>L: Vector query [1024-dim]
    
    L->>VDB: Buscar chunks similares
    VDB-->>L: Top-3:<br/>1. Descripción imagen (score: 0.89)<br/>2. Texto sobre DeepEncoder (0.82)<br/>3. Tabla de componentes (0.76)
    
    L->>G: Buscar nodo DeepEncoder
    G-->>L: Encontrado + relaciones:<br/>uses SAM-base, uses CLIP-large
    
    L->>K: Obtener contenido completo
    K-->>L: Descripción detallada de imagen +<br/>metadata (página, posición)
    
    L->>L: 🤖 Qwen3 14B<br/>Generar respuesta con contexto
    Note over L: Context incluye:<br/>- Descripción generada por Vision<br/>- Entidades relacionadas del grafo<br/>- Texto cercano en documento
    
    L-->>U: DeepEncoder es una arquitectura<br/>multi-capa que integra SAM-base<br/>y CLIP-large. Como se muestra<br/>en la Figura 2 página 3
    
    Note over U: ✅ Respuesta basada en<br/>contenido visual analizado<br/>por Vision Model
```

---

## 📊 Métricas del Sistema

### Performance

| Métrica | Fase 1 (Indexación) | Fase 2 (Query) |
|---------|---------------------|----------------|
| **Tiempo total** | ~140 segundos | ~12 segundos |
| **Llamadas LLM** | 18 (Qwen3) | 1 (Qwen3) |
| **Llamadas Embedding** | 18 (BGE-M3) | 1 (BGE-M3) |
| **Llamadas Vision** | 5 (Nemotron) | 0 |
| **Chunks procesados** | 13 texto + 5 multimodal | - |
| **Nodos en grafo** | 199 | - |
| **Edges en grafo** | 364 | - |
| **Storage size** | ~15 MB | - |

### Costos (Estimados)

| Servicio | Fase 1 | Fase 2 | Costo Unitario |
|----------|--------|--------|----------------|
| **Ollama (local)** | Gratis | Gratis | $0 |
| **OpenRouter Vision** | 5 llamadas | 0 | ~$0.005/imagen |
| **Total por documento** | ~$0.025 | ~$0.00 | - |

---

## 🎯 Puntos Clave para la Clase

### 1. **Chunking Inteligente**
- No es corte arbitrario, respeta semántica
- Overlap para mantener contexto
- ~1200 tokens por chunk

### 2. **Triple Storage**
- Vector DB: búsqueda por similitud
- Knowledge Graph: relaciones semánticas
- KV Store: datos crudos y metadata

### 3. **Modelos Especializados**
- LLM: razonamiento y extracción
- Embeddings: vectorización eficiente
- Vision: análisis multimodal

### 4. **Hybrid Search**
- Combina 3 estrategias diferentes
- Mejor recall que un solo método
- Re-ranking para mejor precision

### 5. **Procesamiento Multimodal**
- Vision model convierte imagen → texto
- Texto se procesa igual que contenido textual
- Unificación en el grafo de conocimiento

---

## 🔧 Comandos Rápidos

```bash
# Indexar documentos
python 1_index_documents.py

# Hacer query
python 2_query_rag.py "¿Qué es DeepSeek-OCR?"

# Visualizar grafo
# Abrir: storage/rag_storage/graph_chunk_entity_relation.graphml en yEd
python fix_graphml_for_yed.py  # Añadir labels primero

# Ver estructura del storage
ls -lh storage/rag_storage/
```

---

## 📚 Recursos Adicionales

- **Documentación LightRAG**: https://github.com/HKUDS/LightRAG
- **RAG-Anything**: https://github.com/HKUDS/RAG-Anything
- **MinerU Parser**: https://github.com/opendatalab/MinerU
- **BGE Embeddings**: https://huggingface.co/BAAI/bge-m3

---

## ✨ Conclusión

Este sistema RAG multimodal combina:
- ✅ Parsing inteligente de documentos complejos
- ✅ Múltiples estrategias de storage (Vector + Graph + KV)
- ✅ Procesamiento especializado por tipo de contenido
- ✅ Búsqueda híbrida de alta calidad
- ✅ Generación de respuestas con contexto rico

**Resultado**: Respuestas precisas que integran texto, imágenes y tablas de forma unificada.

