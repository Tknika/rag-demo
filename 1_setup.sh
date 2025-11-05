#!/bin/bash

echo "=== Instalando dependencias base ==="
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --break-system-packages

echo "=== Instalando RAG-Anything ==="
uv pip install raganything --break-system-packages

echo "=== Fixing NumPy compatibility with MinerU ==="
uv pip install "numpy<2" --break-system-packages

echo "=== Instalando transformers y aceleradores ==="
uv pip install transformers accelerate bitsandbytes sentencepiece --break-system-packages

echo "=== Instalando sentence-transformers para embeddings ==="
uv pip install sentence-transformers --break-system-packages

echo "=== Verificando instalación de MinerU ==="
mineru --version

echo "=== Verificando CUDA ==="
python -c "import torch; print(f'CUDA disponible: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No disponible"}')"

echo "=== Setup completado ==="
