import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))

from raganything import RAGAnything, RAGAnythingConfig
from src.models import (
    create_ollama_llm_func,
    create_ollama_embed_func,
    create_openrouter_vision_func
)
from src.utils import load_config, get_pdf_files, ensure_directories


async def main():
    print("=" * 60)
    print("FASE 1: INDEXACIÓN DE DOCUMENTOS")
    print("=" * 60)
    
    load_dotenv()
    config = load_config()
    ensure_directories(config)
    
    print("\n[1/5] Inicializando modelos...")
    
    llm_func = create_ollama_llm_func(
        config['ollama']['llm_model'],
        config['ollama']['base_url']
    )
    print(f"  ✓ LLM: {config['ollama']['llm_model']} (Ollama)")
    
    embed_func = create_ollama_embed_func(
        config['ollama']['embedding_model'],
        config['ollama']['base_url']
    )
    print(f"  ✓ Embeddings: {config['ollama']['embedding_model']} (Ollama)")
    
    vision_func = create_openrouter_vision_func(
        config['openrouter']['vision_model'],
        config['openrouter']['base_url']
    )
    print(f"  ✓ Vision: {config['openrouter']['vision_model']} (OpenRouter)")
    
    print("\n[2/5] Configurando RAGAnything...")
    
    rag_config = RAGAnythingConfig(
        working_dir=config['paths']['storage_dir'],
        parser="mineru",
        parse_method=config['mineru']['parse_method'],
        enable_image_processing=config['rag']['enable_image_processing'],
        enable_table_processing=config['rag']['enable_table_processing'],
        enable_equation_processing=config['rag']['enable_equation_processing'],
    )
    
    print(f"  ✓ Parser: MinerU ({config['mineru']['parse_method']})")
    print(f"  ✓ Storage: {config['paths']['storage_dir']}")
    
    print("\n[3/5] Inicializando RAG...")
    
    rag = RAGAnything(
        config=rag_config,
        llm_model_func=llm_func,
        embedding_func=embed_func,
        vision_model_func=vision_func,
        lightrag_kwargs={
            'working_dir': config['paths']['storage_dir']
        }
    )
    
    print("  ✓ RAG inicializado")
    
    print("\n[4/5] Escaneando directorio de entrada...")
    
    pdf_files = get_pdf_files(config['paths']['input_dir'])
    
    if not pdf_files:
        print(f"  ⚠ No se encontraron archivos PDF en {config['paths']['input_dir']}")
        print("  → Coloca archivos PDF en ese directorio y ejecuta nuevamente")
        return
    
    print(f"  ✓ Encontrados {len(pdf_files)} archivos PDF")
    
    print("\n[5/5] Procesando documentos...")
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n  [{i}/{len(pdf_files)}] Procesando: {pdf_path.name}")
        print(f"      → Extrayendo contenido con MinerU...")
        
        try:
            await rag.process_document_complete(file_path=str(pdf_path))
            print(f"      ✓ Documento indexado correctamente")
        except Exception as e:
            print(f"      ✗ Error al procesar: {str(e)}")
            continue
    
    print("\n" + "=" * 60)
    print(f"✓ INDEXACIÓN COMPLETADA")
    print(f"  Total documentos procesados: {len(pdf_files)}")
    print(f"  Base de datos en: {config['paths']['storage_dir']}")
    print("=" * 60)
    print("\nAhora puedes ejecutar queries con:")
    print("  python 2_query_rag.py 'tu pregunta aquí'")


if __name__ == "__main__":
    asyncio.run(main())
