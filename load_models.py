import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel, BitsAndBytesConfig, Qwen2VLForConditionalGeneration, AutoProcessor
from sentence_transformers import SentenceTransformer
from config import LLM_MODEL, VISION_MODEL, EMBEDDING_MODEL, DEVICE, LOAD_IN_4BIT

class ModelLoader:
    """Carga y gestiona modelos locales en GPU"""
    
    def __init__(self):
        self.llm_model = None
        self.llm_tokenizer = None
        self.vision_model = None
        self.vision_processor = None
        self.embedding_model = None
        
    def load_llm(self):
        """Carga Qwen-2.5-8B para texto"""
        print(f"=== Cargando LLM: {LLM_MODEL} ===")
        
        if LOAD_IN_4BIT:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        else:
            quantization_config = None
        
        self.llm_tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        print(f"LLM cargado. Memoria GPU: {torch.cuda.memory_allocated(0) / 1024**3:.2f}GB")
        
    def load_vision_model(self):
        """Carga QwenVL para imágenes"""
        print(f"=== Cargando Vision Model: {VISION_MODEL} ===")
        
        if LOAD_IN_4BIT:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        else:
            quantization_config = None
        
        self.vision_processor = AutoProcessor.from_pretrained(VISION_MODEL, trust_remote_code=True)
        self.vision_model = Qwen2VLForConditionalGeneration.from_pretrained(
            VISION_MODEL,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        print(f"Vision Model cargado. Memoria GPU: {torch.cuda.memory_allocated(0) / 1024**3:.2f}GB")
        
    def load_embeddings(self):
        """Carga bge-m3 para embeddings"""
        print(f"=== Cargando Embeddings: {EMBEDDING_MODEL} ===")
        
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL, device=DEVICE)
        
        print(f"Embeddings cargados. Memoria GPU: {torch.cuda.memory_allocated(0) / 1024**3:.2f}GB")
        
    def unload_vision_model(self):
        """Descarga vision model para liberar VRAM"""
        print("=== Descargando Vision Model ===")
        if self.vision_model is not None:
            del self.vision_model
            del self.vision_processor
            self.vision_model = None
            self.vision_processor = None
            torch.cuda.empty_cache()
            print(f"Vision Model descargado. Memoria GPU: {torch.cuda.memory_allocated(0) / 1024**3:.2f}GB")
    
    def get_memory_usage(self):
        """Muestra uso de memoria GPU"""
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        print(f"Memoria GPU - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")
        return allocated, reserved

if __name__ == "__main__":
    print("=== FASE 3: Cargando modelos ===")
    
    loader = ModelLoader()
    
    # Cargar todos los modelos
    loader.load_llm()
    loader.load_vision_model()
    loader.load_embeddings()
    
    print("\n=== Todos los modelos cargados ===")
    loader.get_memory_usage()
    
    # Test rápido
    print("\n=== Test LLM ===")
    test_prompt = "Hola, ¿cómo estás?"
    inputs = loader.llm_tokenizer(test_prompt, return_tensors="pt").to(loader.llm_model.device)
    outputs = loader.llm_model.generate(**inputs, max_new_tokens=20)
    response = loader.llm_tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response}")
    
    print("\n=== Test Embeddings ===")
    embeddings = loader.embedding_model.encode(["Este es un texto de prueba en español"])
    print(f"Shape: {embeddings.shape}")
    print(f"Primeros 5 valores: {embeddings[0][:5]}")
