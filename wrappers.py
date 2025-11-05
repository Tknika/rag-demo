import torch
import base64
from typing import List
from PIL import Image
from io import BytesIO

class LocalModelWrappers:
    """Wrappers que adaptan modelos locales a la interfaz de RAGAnything"""
    
    def __init__(self, model_loader):
        self.model_loader = model_loader
        
    async def llm_wrapper(self, prompt, system_prompt=None, history_messages=[], **kwargs):
        """
        Wrapper para Qwen-2.5-8B que imita openai_complete_if_cache (async)
        """
        import asyncio
        
        def _generate():
            # Construir el prompt completo
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            for msg in history_messages:
                messages.append(msg)
            
            messages.append({"role": "user", "content": prompt})
            
            # Aplicar chat template
            text = self.model_loader.llm_tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Tokenizar
            inputs = self.model_loader.llm_tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=4096
            ).to(self.model_loader.llm_model.device)
            
            # Generar
            with torch.no_grad():
                outputs = self.model_loader.llm_model.generate(
                    **inputs,
                    max_new_tokens=kwargs.get('max_tokens', 512),
                    temperature=kwargs.get('temperature', 0.2),
                    top_p=kwargs.get('top_p', 0.9),
                    do_sample=True,
                    pad_token_id=self.model_loader.llm_tokenizer.eos_token_id
                )
            
            # Decodificar
            response = self.model_loader.llm_tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            return response
        
        # Ejecutar en thread para no bloquear el loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _generate)
    
    async def vision_wrapper(self, prompt, system_prompt=None, history_messages=[], 
                       image_data=None, messages=None, **kwargs):
        """
        Wrapper para QwenVL que procesa imágenes (async)
        """
        import asyncio
        
        # Si no hay imagen, usar LLM normal
        if not image_data and not messages:
            return await self.llm_wrapper(prompt, system_prompt, history_messages, **kwargs)
        
        def _generate_vision():
            # Procesar imagen desde base64
            if image_data:
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
            
            # Construir query para vision model
            query = self.model_loader.vision_processor.from_list_format([
                {'image': image},
                {'text': prompt},
            ])
            
            # Generar respuesta
            with torch.no_grad():
                response, _ = self.model_loader.vision_model.chat(
                    self.model_loader.vision_processor,
                    query=query,
                    history=None
                )
            
            return response
        
        # Ejecutar en thread para no bloquear el loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _generate_vision)
    
    async def embedding_wrapper(self, texts: List[str]) -> List[List[float]]:
        """
        Wrapper para bge-m3 embeddings (async)
        """
        # Ejecutar encode en thread para no bloquear el loop
        import asyncio
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model_loader.embedding_model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                convert_to_numpy=True
            )
        )
        
        return embeddings.tolist()

def create_embedding_func(model_loader):
    """
    Crea EmbeddingFunc compatible con RAGAnything
    """
    from lightrag.utils import EmbeddingFunc
    
    wrapper = LocalModelWrappers(model_loader)
    
    embedding_func = EmbeddingFunc(
        embedding_dim=1024,  # bge-m3 dimension
        max_token_size=8192,
        func=wrapper.embedding_wrapper
    )
    
    return embedding_func

if __name__ == "__main__":
    import asyncio
    import importlib.util
    import sys
    
    # Load module from file with number prefix
    spec = importlib.util.spec_from_file_location("load_models_module", "load_models.py")
    load_models_module = importlib.util.module_from_spec(spec)
    sys.modules["load_models_module"] = load_models_module
    spec.loader.exec_module(load_models_module)
    ModelLoader = load_models_module.ModelLoader
    
    async def test_wrappers():
        print("=== FASE 4: Testeando wrappers ===")
        
        # Cargar modelos
        loader = ModelLoader()
        loader.load_llm()
        loader.load_embeddings()
        
        # Crear wrappers
        wrappers = LocalModelWrappers(loader)
        
        # Test LLM wrapper
        print("\n=== Test LLM Wrapper ===")
        response = await wrappers.llm_wrapper(
            "¿Cuál es la capital de España?",
            system_prompt="Eres un asistente útil."
        )
        print(f"Response: {response}")
        
        # Test embedding wrapper
        print("\n=== Test Embedding Wrapper ===")
        texts = ["Texto de prueba en español", "Otro ejemplo"]
        embeddings = await wrappers.embedding_wrapper(texts)
        print(f"Número de textos: {len(embeddings)}")
        print(f"Dimensión: {len(embeddings[0])}")
        print(f"Primeros 5 valores del primer embedding: {embeddings[0][:5]}")
    
    asyncio.run(test_wrappers())
