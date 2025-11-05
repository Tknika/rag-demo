#!/usr/bin/env python
"""
Script de ejemplo completo que ejecuta todo el pipeline RAG
"""

import asyncio
import sys
from pathlib import Path

# Añadir el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from config import PDF_PATH
from load_models import ModelLoader
from wrappers import LocalModelWrappers, create_embedding_func
from raganything import RAGAnything, RAGAnythingConfig

async def full_pipeline_example():
    """
    Ejemplo completo: procesa documento y hace queries
    """
    
    print("=" * 80)
    print("EJEMPLO COMPLETO: RAG-Anything + HuggingFace Local")
    print("=" * 80)
    
    # Verificar que existe el PDF
    if not Path(PDF_PATH).exists():
        print(f"\nError: No se encontró el PDF en {PDF_PATH}")
        print("Edita config.py y configura PDF_PATH con tu documento")
        return
    
    # ========== FASE 1: CARGAR MODELOS ==========
    print("\n[FASE 1/3] CARGANDO MODELOS")
    print("-" * 80)
    
    loader = ModelLoader()
    loader.load_llm()
    loader.load_vision_model()
    loader.load_embeddings()
    
    print(f"\nModelos cargados correctamente")
    loader.get_memory_usage()
    
    # ========== FASE 2: PROCESAR DOCUMENTO ==========
    print("\n[FASE 2/3] PROCESANDO DOCUMENTO")
    print("-" * 80)
    print(f"Documento: {PDF_PATH}")
    print("Esto puede tardar varios minutos...\n")
    
    # Crear wrappers
    wrappers = LocalModelWrappers(loader)
    embedding_func = create_embedding_func(loader)
    
    # Configurar RAGAnything
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser="mineru",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=False,
    )
    
    # Inicializar y procesar
    rag = RAGAnything(
        config=config,
        llm_model_func=wrappers.llm_wrapper,
        vision_model_func=wrappers.vision_wrapper,
        embedding_func=embedding_func,
    )
    
    try:
        await rag.process_document_complete(
            file_path=PDF_PATH,
            output_dir="./output",
            parse_method="auto",
            display_stats=True
        )
        print("\nDocumento procesado exitosamente")
        
    except Exception as e:
        print(f"\nError procesando documento: {e}")
        return
    
    # Liberar Vision Model
    loader.unload_vision_model()
    print("\nVision Model descargado (no necesario para queries)")
    loader.get_memory_usage()
    
    # ========== FASE 3: QUERIES DE EJEMPLO ==========
    print("\n[FASE 3/3] QUERIES DE EJEMPLO")
    print("-" * 80)
    
    queries = [
        "¿Cuál es el tema principal del documento?",
        "Resume el contenido en 3 puntos clave",
    ]
    
    for i, question in enumerate(queries, 1):
        print(f"\nQuery {i}: {question}")
        print("-" * 80)
        
        result = await rag.aquery(question, mode="hybrid")
        
        print("RESPUESTA:")
        print(result)
        print("\n" + "=" * 80)
    
    print("\n✓ Pipeline completado exitosamente")
    print(f"✓ Knowledge graph guardado en: ./rag_storage")
    print(f"✓ Para más queries ejecuta: python query.py --interactive")

if __name__ == "__main__":
    print("\nIniciando pipeline RAG...\n")
    asyncio.run(full_pipeline_example())
