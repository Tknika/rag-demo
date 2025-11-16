# Guía de Inicio Rápido

## Setup Inicial (5 minutos)

### 1. Instalar Ollama

```bash
# En Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Iniciar servicio
ollama serve
```

### 2. Descargar Modelos en Ollama

```bash
# En otra terminal
ollama pull qwen2.5:8b
ollama pull bge-m3

# Verificar instalación
ollama list
```

### 3. Clonar y Setup del Proyecto

```bash
cd rag-multimodal-poc
pip install -r requirements.txt
```

### 4. Configurar OpenRouter API Key

Editar `.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-tu-key-real-aqui
```

Obtener key en: https://openrouter.ai/keys

## Ejemplo Completo

### Paso 1: Preparar Documento de Prueba

Colocar un PDF con texto, tablas e imágenes en `data/input/`:

```bash
cp ~/mi_documento.pdf data/input/
```

### Paso 2: Indexar Documentos

```bash
python 1_index_documents.py
```

**Salida esperada:**
```
============================================================
FASE 1: INDEXACIÓN DE DOCUMENTOS
============================================================

[1/5] Inicializando modelos...
  ✓ LLM: qwen2.5:8b (Ollama)
  ✓ Embeddings: bge-m3 (Ollama)
  ✓ Vision: nvidia/nemotron-nano-12b-v2-vl (OpenRouter)

[2/5] Configurando RAGAnything...
  ✓ Parser: MinerU (auto)
  ✓ Storage: ./storage/rag_storage

[3/5] Inicializando RAG...
  ✓ RAG inicializado

[4/5] Escaneando directorio de entrada...
  ✓ Encontrados 1 archivos PDF

[5/5] Procesando documentos...

  [1/1] Procesando: mi_documento.pdf
      → Extrayendo contenido con MinerU...
      ✓ Documento indexado correctamente

============================================================
✓ INDEXACIÓN COMPLETADA
  Total documentos procesados: 1
  Base de datos en: ./storage/rag_storage
============================================================

Ahora puedes ejecutar queries con:
  python 2_query_rag.py 'tu pregunta aquí'
```

### Paso 3: Realizar Queries

**Query 1: Pregunta general sobre el documento**

```bash
python 2_query_rag.py "Resume el contenido del documento"
```

**Query 2: Pregunta sobre tabla específica**

```bash
python 2_query_rag.py "¿Cuáles son los resultados mostrados en la tabla de ventas?"
```

**Query 3: Pregunta sobre imagen/diagrama**

```bash
python 2_query_rag.py "Explica qué muestra el diagrama del capítulo 2"
```

**Salida esperada:**
```
============================================================
FASE 2: QUERY RAG
============================================================

[1/3] Cargando modelos...
  ✓ Modelos cargados

[2/3] Conectando a base de datos RAG...
  ✓ RAG cargado desde storage

[3/3] Ejecutando query...

🔍 Query: Explica qué muestra el diagrama del capítulo 2

------------------------------------------------------------

📝 Respuesta:

El diagrama del capítulo 2 muestra el flujo de procesamiento 
de un sistema RAG multimodal. En la parte superior se observa 
la entrada de documentos PDF, que pasan por un parser (MinerU) 
que extrae texto, tablas e imágenes...

[Respuesta generada por el modelo basada en el contenido]

------------------------------------------------------------

============================================================
```

## Casos de Uso Comunes

### 1. Documento Técnico con Diagramas

```bash
# Indexar
python 1_index_documents.py

# Queries específicas
python 2_query_rag.py "Explica la arquitectura del sistema"
python 2_query_rag.py "¿Qué componentes se muestran en el diagrama de la figura 3?"
python 2_query_rag.py "Resume las especificaciones técnicas"
```

### 2. Report con Tablas de Datos

```bash
python 2_query_rag.py "¿Cuáles son los valores máximos en la tabla de resultados?"
python 2_query_rag.py "Compara los datos del Q1 vs Q2"
python 2_query_rag.py "¿Qué tendencias se observan en los datos?"
```

### 3. Paper Académico

```bash
python 2_query_rag.py "¿Cuál es la metodología propuesta?"
python 2_query_rag.py "Resume los resultados experimentales"
python 2_query_rag.py "Explica las gráficas de comparación"
```

## Troubleshooting Rápido

### Error: "Connection refused" (Ollama)

```bash
# Verificar que Ollama está corriendo
ps aux | grep ollama

# Iniciar si no está activo
ollama serve
```

### Error: "Model not found"

```bash
# Listar modelos instalados
ollama list

# Instalar el que falta
ollama pull qwen2.5:8b
ollama pull bge-m3
```

### Error: "OPENROUTER_API_KEY not found"

```bash
# Verificar que .env existe y tiene la key
cat .env

# Si no existe, crear
echo "OPENROUTER_API_KEY=tu-key-aqui" > .env
```

### Error al procesar PDF

```bash
# Verificar que el PDF no está corrupto
file data/input/mi_documento.pdf

# Verificar permisos
ls -la data/input/
```

### Procesamiento lento

**Solución 1: Usar GPU si disponible**

Editar `config/config.yaml`:
```yaml
mineru:
  device: "cuda"  # Cambiar de "cpu" a "cuda"
```

**Solución 2: Reducir documentos de prueba**

```bash
# Mover documentos pesados fuera del input
mv data/input/*.pdf /tmp/
# Probar solo con 1-2 documentos ligeros
```

## Tips y Mejores Prácticas

### 1. Organización de Documentos

```bash
data/input/
├── categoria1/
│   ├── doc1.pdf
│   └── doc2.pdf
└── categoria2/
    └── doc3.pdf
```

### 2. Re-indexación Incremental

```bash
# Agregar nuevos documentos sin borrar índice existente
cp nuevos_docs/*.pdf data/input/
python 1_index_documents.py
```

### 3. Limpiar y Empezar de Cero

```bash
# Borrar índice completo
rm -rf storage/rag_storage/

# Re-indexar todo
python 1_index_documents.py
```

### 4. Diferentes Modos de Query

Los modos disponibles son:
- **hybrid** (recomendado): Combina búsqueda vectorial + knowledge graph
- **local**: Solo búsqueda local/específica
- **global**: Búsqueda global en todo el corpus
- **naive**: Búsqueda simple por similitud

Para cambiar el modo, editar en `2_query_rag.py` línea 60:
```python
result = await rag.aquery(query, mode="global")  # Cambiar aquí
```

### 5. Monitoreo de Uso

```bash
# Ver tamaño del storage
du -sh storage/rag_storage/

# Ver cantidad de archivos procesados
ls data/input/ | wc -l
```

## Próximos Pasos

1. Experimentar con diferentes tipos de PDFs
2. Probar queries complejas con múltiples condiciones
3. Ajustar parámetros en `config/config.yaml` según tus necesidades
4. Explorar la documentación de RAG-Anything para features avanzadas
5. Considerar implementar UI web con Streamlit

## Recursos Adicionales

- **RAG-Anything Docs:** https://github.com/HKUDS/RAG-Anything
- **LightRAG Docs:** https://github.com/HKUDS/LightRAG
- **Ollama Docs:** https://ollama.com/docs
- **OpenRouter:** https://openrouter.ai/docs
