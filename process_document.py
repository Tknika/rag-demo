import asyncio
import os
import torch
from raganything import RAGAnything, RAGAnythingConfig
from load_models import ModelLoader
from wrappers import LocalModelWrappers, create_embedding_func

from config import (
    PDF_PATH, OUTPUT_DIR, WORKING_DIR, PARSED_OUTPUT,
    ENABLE_IMAGE_PROCESSING, ENABLE_TABLE_PROCESSING, ENABLE_EQUATION_PROCESSING,
    MINERU_PARSE_METHOD, MINERU_DEVICE
)

async def process_document():
    """
    Procesa el documento PDF y construye el knowledge graph multimodal
    
    Estrategia de memoria:
    1. Cargar LLM + Vision + Embeddings (~18-19GB)
    2. MinerU usa CPU para parsing (config.MINERU_DEVICE = "cpu")
    3. Los modelos permanecen en GPU durante todo el proceso
    
    Nota: process_document_complete() hace parsing Y procesamiento en una sola llamada,
    por lo que los modelos deben estar cargados durante toda la ejecución.
    """
    
    print("=== FASE 5: Procesando documento con RAGAnything ===")
    
    # 1. Cargar todos los modelos necesarios
    print("\n[1/4] Cargando modelos...")
    loader = ModelLoader()
    loader.load_llm()
    loader.load_embeddings()
    
    # Cargar vision model si está habilitado el procesamiento de imágenes
    if ENABLE_IMAGE_PROCESSING:
        loader.load_vision_model()
    
    torch.cuda.empty_cache()
    print("Modelos cargados:")
    loader.get_memory_usage()
    
    # 2. Crear wrappers
    print("\n[2/4] Creando wrappers...")
    wrappers = LocalModelWrappers(loader)
    embedding_func = create_embedding_func(loader)
    
    # 3. Configurar e inicializar RAGAnything
    print("\n[3/4] Configurando RAGAnything...")
    config = RAGAnythingConfig(
        working_dir=WORKING_DIR,
        parser="mineru",
        parse_method=MINERU_PARSE_METHOD,
        enable_image_processing=ENABLE_IMAGE_PROCESSING,
        enable_table_processing=ENABLE_TABLE_PROCESSING,
        enable_equation_processing=ENABLE_EQUATION_PROCESSING,
    )
    
    rag = RAGAnything(
        config=config,
        llm_model_func=wrappers.llm_wrapper,
        vision_model_func=wrappers.vision_wrapper,
        embedding_func=embedding_func,
    )
    
    # 4. Procesar documento
    print(f"\n[4/4] Procesando documento: {PDF_PATH}")
    print(f"MinerU usará {MINERU_DEVICE.upper()} para parsing")
    print("NOTA: Los modelos deben permanecer cargados para el procesamiento posterior")
    
    # Limpiar caché pero mantener modelos cargados
    torch.cuda.empty_cache()
    loader.get_memory_usage()
    
    # Ocultar GPU para subprocesos (MinerU) si se configuró CPU
    original_cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES')
    if MINERU_DEVICE == "cpu":
        print("Ocultando GPU para MinerU subprocess...")
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
    
    try:
        await rag.process_document_complete(
            file_path=PDF_PATH,
            output_dir=OUTPUT_DIR,
            parse_method=MINERU_PARSE_METHOD,
            display_stats=True
        )
        
        print("\n=== Documento procesado ===")
        
        # Limpiar caché
        torch.cuda.empty_cache()
        loader.get_memory_usage()
        
        print("\n=== Documento procesado exitosamente ===")
        print(f"Knowledge graph guardado en: {WORKING_DIR}")
        
    except Exception as e:
        print(f"\nError procesando documento: {e}")
        raise
    
    finally:
        # Restaurar visibilidad de GPU
        if MINERU_DEVICE == "cpu":
            if original_cuda_visible is not None:
                os.environ['CUDA_VISIBLE_DEVICES'] = original_cuda_visible
            else:
                os.environ.pop('CUDA_VISIBLE_DEVICES', None)
        
        # Limpiar caché final
        torch.cuda.empty_cache()
        print("\n=== Memoria final ===")
        loader.get_memory_usage()
    
    return rag, loader

if __name__ == "__main__":
    rag, loader = asyncio.run(process_document())
    
    print("\n=== Sistema listo para queries ===")
    print(f"Memoria GPU final: {loader.get_memory_usage()[0]:.2f}GB")
