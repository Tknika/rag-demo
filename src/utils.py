import yaml
from pathlib import Path
from typing import Dict, List

def load_config(config_path: str = "./config/config.yaml") -> Dict:
    """Carga la configuración desde archivo YAML"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_pdf_files(directory: str) -> List[Path]:
    """Obtiene todos los archivos PDF de un directorio"""
    path = Path(directory)
    if not path.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {directory}")
    return list(path.glob("*.pdf"))

def ensure_directories(config: Dict) -> None:
    """Crea los directorios necesarios si no existen"""
    for key, path in config['paths'].items():
        Path(path).mkdir(parents=True, exist_ok=True)
