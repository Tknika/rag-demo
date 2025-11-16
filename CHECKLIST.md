# Checklist de Verificación

## Pre-requisitos

### ✓ Sistema

- [ ] Python 3.10 o superior instalado
  ```bash
  python --version
  ```

- [ ] Ollama instalado y ejecutando
  ```bash
  ollama --version
  ollama serve  # Debe estar corriendo
  ```

### ✓ Modelos Ollama

- [ ] Qwen 2.5 8B descargado
  ```bash
  ollama list | grep qwen2.5:8b
  ```
  Si no está: `ollama pull qwen2.5:8b`

- [ ] bge-m3 descargado
  ```bash
  ollama list | grep bge-m3
  ```
  Si no está: `ollama pull bge-m3`

### ✓ Dependencias Python

- [ ] Dependencias instaladas
  ```bash
  cd rag-multimodal-poc
  pip install -r requirements.txt
  ```

- [ ] Verificar instalación de raganything
  ```bash
  python -c "from raganything import RAGAnything; print('OK')"
  ```

### ✓ Configuración

- [ ] Archivo `.env` existe con API key
  ```bash
  cat .env
  # Debe mostrar: OPENROUTER_API_KEY=sk-or-...
  ```

- [ ] Archivo `config/config.yaml` configurado correctamente
  ```bash
  cat config/config.yaml
  ```

- [ ] Directorios creados
  ```bash
  ls -la data/input data/processed storage
  ```

### ✓ Documentos

- [ ] PDFs colocados en `data/input/`
  ```bash
  ls data/input/*.pdf
  ```

## Test de Conexiones

### ✓ Ollama LLM

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:8b",
  "prompt": "Hello",
  "stream": false
}'
```

Debe retornar JSON con respuesta del modelo.

### ✓ Ollama Embeddings

```bash
curl http://localhost:11434/api/embeddings -d '{
  "model": "bge-m3",
  "prompt": "test"
}'
```

Debe retornar array de números (embeddings).

### ✓ OpenRouter API

```bash
export OPENROUTER_API_KEY="tu-key-aqui"

curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

Debe retornar lista de modelos disponibles.

## Verificación de Código

### ✓ Imports

```bash
python -c "
from raganything import RAGAnything, RAGAnythingConfig
from src.models import create_ollama_llm_func, create_ollama_embed_func, create_openrouter_vision_func
from src.utils import load_config
print('✓ Todos los imports correctos')
"
```

### ✓ Configuración cargable

```bash
python -c "
from src.utils import load_config
config = load_config()
print('✓ Config cargada:', config.keys())
"
```

## Test de Indexación

### ✓ Prueba con PDF de test

```bash
# Colocar un PDF pequeño en data/input/
# Ejecutar indexación
python 1_index_documents.py
```

**Éxito esperado:**
- Sin errores en consola
- Directorio `storage/rag_storage/` creado con contenido
- Mensaje final: "✓ INDEXACIÓN COMPLETADA"

### ✓ Verificar storage

```bash
ls -lh storage/rag_storage/
```

Debe contener archivos creados por LightRAG.

## Test de Query

### ✓ Query simple

```bash
python 2_query_rag.py "Resume el documento"
```

**Éxito esperado:**
- Sin errores
- Respuesta coherente generada

### ✓ Query con tabla

```bash
python 2_query_rag.py "¿Hay tablas en el documento?"
```

### ✓ Query con imagen

```bash
python 2_query_rag.py "¿Hay imágenes o diagramas?"
```

## Checklist de Errores Comunes

### Si falla la indexación:

- [ ] Verificar que Ollama está corriendo: `ps aux | grep ollama`
- [ ] Verificar que los PDFs no están corruptos: `file data/input/*.pdf`
- [ ] Verificar espacio en disco: `df -h`
- [ ] Ver logs de error completos en consola

### Si falla la query:

- [ ] Verificar que storage/ existe: `ls storage/rag_storage/`
- [ ] Verificar que se indexó al menos 1 documento
- [ ] Verificar OPENROUTER_API_KEY en .env
- [ ] Probar con query más simple: "Hola"

### Si es muy lento:

- [ ] Cambiar `device: "cuda"` en config.yaml (si tienes GPU)
- [ ] Reducir número de PDFs para prueba inicial
- [ ] Verificar uso de RAM: `free -h`
- [ ] Verificar uso de CPU: `top`

## Métricas de Éxito

### Indexación exitosa:

- ✓ Tiempo: ~30-60 segundos por PDF (depende del tamaño)
- ✓ Storage size: ~10-50 MB por documento
- ✓ Sin errores en logs

### Query exitosa:

- ✓ Tiempo respuesta: 5-15 segundos
- ✓ Respuesta coherente y relevante
- ✓ Referencias correctas al contenido

## Siguiente Nivel

Una vez que todo funciona:

- [ ] Agregar más documentos y re-indexar
- [ ] Experimentar con diferentes tipos de queries
- [ ] Ajustar parámetros en config.yaml
- [ ] Probar diferentes modos de query (hybrid/local/global)
- [ ] Explorar features avanzadas en ARQUITECTURA.md

## Soporte

Si algo no funciona después de este checklist:

1. Revisar logs de error completos
2. Verificar versiones de dependencias
3. Consultar documentación oficial de RAG-Anything
4. Verificar issues en GitHub del proyecto

## Notas Finales

- Primera ejecución descarga modelos de MinerU (~2GB)
- Indexación es one-time, queries son rápidas
- Mantén Ollama corriendo mientras usas el sistema
- OpenRouter se cobra por tokens usados (vision model)
