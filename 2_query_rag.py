import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))

from raganything import RAGAnything, RAGAnythingConfig
from lightrag import LightRAG, QueryParam
from src.models import (
    create_ollama_llm_func,
    create_ollama_embed_func,
    create_openrouter_vision_func
)
from src.utils import load_config


async def main(query: str):
    print("=" * 60)
    print("FASE 2: QUERY RAG")
    print("=" * 60)
    
    load_dotenv()
    config = load_config()
    
    storage_path = Path(config['paths']['storage_dir'])
    if not storage_path.exists():
        print("\n✗ Error: Base de datos no encontrada")
        print("  → Ejecuta primero: python 1_index_documents.py")
        return
    
    print("\n[1/3] Cargando modelos...")
    
    llm_func = create_ollama_llm_func(
        config['ollama']['llm_model'],
        config['ollama']['base_url']
    )
    
    embed_func = create_ollama_embed_func(
        config['ollama']['embedding_model'],
        config['ollama']['base_url']
    )
    
    vision_func = create_openrouter_vision_func(
        config['openrouter']['vision_model'],
        config['openrouter']['base_url']
    )
    
    print("  ✓ Modelos cargados")
    
    print("\n[2/3] Conectando a base de datos RAG...")
    
    # Crear LightRAG explícitamente desde storage existente
    lightrag = LightRAG(
        working_dir=config['paths']['storage_dir'],
        llm_model_func=llm_func,
        embedding_func=embed_func  # EmbeddingFunc completo (tiene .func, .embedding_dim, .max_token_size)
    )
    
    print("  ✓ LightRAG cargado desde storage")
    
    # Crear RAGAnything con LightRAG pre-inicializado
    rag_config = RAGAnythingConfig(
        working_dir=config['paths']['storage_dir'],
        parser="mineru",
        parse_method=config['mineru']['parse_method'],
        enable_image_processing=config['rag']['enable_image_processing'],
        enable_table_processing=config['rag']['enable_table_processing'],
        enable_equation_processing=config['rag']['enable_equation_processing'],
    )
    
    rag = RAGAnything(
        config=rag_config,
        lightrag=lightrag,  # Pasar instancia pre-creada
        vision_model_func=vision_func
    )
    
    print("  ✓ RAG multimodal conectado")
    
    print("\n[3/3] Ejecutando query...")
    print(f"\n🔍 Query: {query}")
    print("\n" + "-" * 60)
    
    try:
        result = await rag.aquery(query, mode="hybrid")
        
        print(f"\n📝 Respuesta:\n")
        print(result)
        print("\n" + "-" * 60)
        
    except Exception as e:
        print(f"\n✗ Error durante la query: {str(e)}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso: python 2_query_rag.py 'tu pregunta aquí'")
        print("\nEjemplos:")
        print("  python 2_query_rag.py '¿Qué dice sobre el tema X?'")
        print("  python 2_query_rag.py 'Resume la tabla de resultados'")
        print("  python 2_query_rag.py 'Explica el diagrama del capítulo 3'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    asyncio.run(main(query))
