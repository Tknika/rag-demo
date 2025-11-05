import asyncio
from raganything import RAGAnything, RAGAnythingConfig
from load_models import ModelLoader
from wrappers import LocalModelWrappers, create_embedding_func
from config import WORKING_DIR
import os

async def setup_rag_for_query():
    """
    Carga el sistema RAG existente para hacer queries
    """
    
    print("=== FASE 6: Inicializando sistema para queries ===")
    
    # Verificar que existe el knowledge graph
    if not os.path.exists(WORKING_DIR):
        raise FileNotFoundError(
            f"No se encontró el knowledge graph en {WORKING_DIR}. "
            "Ejecuta primero 5_process_document.py"
        )
    
    # Cargar solo los modelos necesarios para query (sin vision model)
    print("\n[1/3] Cargando modelos (LLM + Embeddings)...")
    loader = ModelLoader()
    loader.load_llm()
    loader.load_embeddings()
    loader.get_memory_usage()
    
    # Crear wrappers
    print("\n[2/3] Creando wrappers...")
    wrappers = LocalModelWrappers(loader)
    embedding_func = create_embedding_func(loader)
    
    # Configurar RAGAnything
    print("\n[3/3] Inicializando RAGAnything...")
    config = RAGAnythingConfig(
        working_dir=WORKING_DIR,
    )
    
    rag = RAGAnything(
        config=config,
        llm_model_func=wrappers.llm_wrapper,
        embedding_func=embedding_func,
    )
    
    print("\n=== Sistema listo para queries ===\n")
    
    return rag

async def query_rag(rag, question: str, mode: str = "hybrid"):
    """
    Hace una query al sistema RAG
    
    Args:
        rag: Instancia de RAGAnything
        question: Pregunta en español
        mode: Modo de retrieval (hybrid, local, global, naive)
    """
    
    print(f"Pregunta: {question}")
    print(f"Modo: {mode}")
    print("\nBuscando respuesta...\n")
    
    result = await rag.aquery(question, mode=mode)
    
    print("=" * 80)
    print("RESPUESTA:")
    print("=" * 80)
    print(result)
    print("=" * 80)
    
    return result

async def interactive_mode():
    """
    Modo interactivo para hacer múltiples queries
    """
    
    rag = await setup_rag_for_query()
    
    print("\n" + "=" * 80)
    print("MODO INTERACTIVO - Escribe tus preguntas")
    print("=" * 80)
    print("Comandos especiales:")
    print("  'salir' o 'exit' - Terminar")
    print("  'modo <tipo>' - Cambiar modo (hybrid, local, global, naive)")
    print("=" * 80 + "\n")
    
    mode = "hybrid"
    
    while True:
        try:
            question = input(f"\n[{mode}] Pregunta: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['salir', 'exit', 'quit']:
                print("\nCerrando sistema...")
                break
            
            if question.lower().startswith('modo '):
                new_mode = question.split(' ', 1)[1].strip()
                if new_mode in ['hybrid', 'local', 'global', 'naive']:
                    mode = new_mode
                    print(f"Modo cambiado a: {mode}")
                else:
                    print("Modo inválido. Usa: hybrid, local, global, naive")
                continue
            
            await query_rag(rag, question, mode)
            
        except KeyboardInterrupt:
            print("\n\nCerrando sistema...")
            break
        except Exception as e:
            print(f"\nError: {e}")

async def single_query_mode():
    """
    Modo de query única para testing
    """
    
    rag = await setup_rag_for_query()
    
    # Ejemplos de queries
    queries = [
        "¿Cuál es el tema principal del documento?",
        "Resume el contenido de las tablas encontradas",
        "¿Qué muestran las imágenes del documento?",
    ]
    
    print("Queries de ejemplo:")
    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Ejecutar primera query como ejemplo
    await query_rag(rag, queries[0], mode="hybrid")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Modo interactivo
        asyncio.run(interactive_mode())
    else:
        # Modo de query única
        print("Uso: python 6_query.py [--interactive]")
        print("Sin argumentos: ejecuta query de ejemplo")
        print("Con --interactive: modo interactivo\n")
        asyncio.run(single_query_mode())
