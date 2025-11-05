import os

# Rutas
PDF_PATH = "docs/BOE-A-2002-18099-consolidado.pdf"
OUTPUT_DIR = "./output"
WORKING_DIR = "./rag_storage"
PARSED_OUTPUT = "./parsed_content"

# Modelos
LLM_MODEL = "Qwen/Qwen3-4B"
VISION_MODEL = "Qwen/Qwen2-VL-2B-Instruct"  
EMBEDDING_MODEL = "BAAI/bge-m3"

# GPU
DEVICE = "cuda"
LOAD_IN_4BIT = True

# MinerU
MINERU_PARSE_METHOD = "auto"  # auto, ocr, txt
MINERU_LANG = "latin"
MINERU_DEVICE = "cpu"  # cpu or cuda - usa CPU para evitar conflictos de VRAM

# RAGAnything
ENABLE_IMAGE_PROCESSING = True
ENABLE_TABLE_PROCESSING = True
ENABLE_EQUATION_PROCESSING = False  

# Crear directorios si no existen
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(WORKING_DIR, exist_ok=True)
os.makedirs(PARSED_OUTPUT, exist_ok=True)
