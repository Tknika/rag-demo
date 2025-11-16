import os
import asyncio
import ollama
import aiohttp
import numpy as np
from typing import List, Optional
from lightrag.utils import EmbeddingFunc


def create_ollama_llm_func(model_name: str, base_url: str):
    """
    Crea función wrapper para LLM via Ollama (Qwen8B)
    Usado para generar respuestas y crear knowledge graph
    """
    async def llm_func(prompt: str, system_prompt: Optional[str] = None, 
                       history_messages: List = [], **kwargs) -> str:
        print(f"🤖 [LLM] Llamando a {model_name} | prompt: {prompt[:80]}...")
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})
        
        # Opciones para mejor adherencia a formato
        default_options = {
            'temperature': 0.1,      # Más determinista
            'top_p': 0.9,            # Más consistente
            'repeat_penalty': 1.1,   # Evita repeticiones
        }
        # Merge con opciones pasadas (las pasadas tienen prioridad)
        options = {**default_options, **kwargs.get('options', {})}
        
        # Ejecutar en thread pool ya que ollama.chat es sincrónico
        response = await asyncio.to_thread(
            ollama.chat,
            model=model_name,
            messages=messages,
            options=options
        )
        
        print(f"✅ [LLM] Respuesta recibida de {model_name}")
        return response['message']['content']
    
    return llm_func


def create_ollama_embed_func(model_name: str, base_url: str) -> EmbeddingFunc:
    """
    Crea función wrapper para embeddings via Ollama (bge-m3)
    Usado para vectorizar texto y búsqueda semántica
    """
    async def embed_func(texts: List[str]) -> np.ndarray:
        print(f"🔢 [EMBED] Llamando a {model_name} | {len(texts)} texto(s)")
        
        embeddings = []
        
        for i, text in enumerate(texts, 1):
            # Ejecutar en thread pool ya que ollama.embeddings es sincrónico
            response = await asyncio.to_thread(
                ollama.embeddings,
                model=model_name,
                prompt=text
            )
            embeddings.append(response['embedding'])
            if len(texts) > 5 and i % 5 == 0:
                print(f"   └─ Procesados {i}/{len(texts)} embeddings...")
        
        print(f"✅ [EMBED] Completado {len(texts)} embeddings con {model_name}")
        return np.array(embeddings)
    
    return EmbeddingFunc(
        embedding_dim=1024,
        max_token_size=8192,
        func=embed_func
    )


def create_openrouter_vision_func(model_name: str, base_url: str):
    """
    Crea función wrapper para Vision LLM via OpenRouter (nvidia/nemotron)
    Usado para analizar imágenes recuperadas del contexto
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY no encontrada en variables de entorno")
    
    async def vision_func(prompt: str, system_prompt: Optional[str] = None,
                         history_messages: List = [], image_data: Optional[str] = None,
                         messages: Optional[List] = None, **kwargs) -> str:
        
        has_image = image_data is not None or (messages and any(
            isinstance(m.get('content'), list) for m in messages
        ))
        image_marker = "📷 [con imagen]" if has_image else "[texto solo]"
        print(f"👁️  [VISION] Llamando a {model_name} {image_marker} | prompt: {prompt[:60]}...")
        
        if messages:
            payload_messages = messages
        else:
            payload_messages = []
            
            if system_prompt:
                payload_messages.append({"role": "system", "content": system_prompt})
            
            payload_messages.extend(history_messages)
            
            if image_data:
                content = [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                    },
                    {"type": "text", "text": prompt}
                ]
                payload_messages.append({"role": "user", "content": content})
            else:
                payload_messages.append({"role": "user", "content": prompt})
        
        # Usar aiohttp para HTTP async
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": payload_messages,
                    **kwargs
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                print(f"✅ [VISION] Respuesta recibida de {model_name}")
                return data['choices'][0]['message']['content']
    
    return vision_func
