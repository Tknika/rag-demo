#!/usr/bin/env python
"""
Script maestro para ejecutar el pipeline completo paso a paso
"""

import subprocess
import sys
from pathlib import Path

def run_script(script_name, description):
    """Ejecuta un script Python y maneja errores"""
    print("\n" + "=" * 80)
    print(f"{description}")
    print("=" * 80 + "\n")
    
    result = subprocess.run([sys.executable, script_name], capture_output=False)
    
    if result.returncode != 0:
        print(f"\nError ejecutando {script_name}")
        sys.exit(1)
    
    print(f"\n✓ {script_name} completado")

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                    RAG-ANYTHING LOCAL PIPELINE                     ║
    ║                   HuggingFace Models + MinerU                      ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar que existe config.py
    if not Path("config.py").exists():
        print("Error: config.py no encontrado")
        sys.exit(1)
    
    # Importar config para verificar PDF_PATH
    from config import PDF_PATH
    
    if not Path(PDF_PATH).exists():
        print(f"\nAdvertencia: PDF no encontrado en {PDF_PATH}")
        print("Edita config.py antes de continuar")
        response = input("\n¿Continuar de todos modos? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    print("\nEste script ejecutará:")
    print("  1. Parse del PDF con MinerU")
    print("  2. Carga y test de modelos")
    print("  3. Test de wrappers")
    print("  4. Procesamiento completo del documento")
    print("  5. Query de ejemplo")
    
    response = input("\n¿Comenzar? (y/n): ")
    if response.lower() != 'y':
        print("Cancelado")
        sys.exit(0)
    
    # Ejecutar pipeline
    steps = [
        ("parse_pdf.py", "PASO 1/5: Parsing PDF con MinerU"),
        ("load_models.py", "PASO 2/5: Cargando y testeando modelos"),
        ("wrappers.py", "PASO 3/5: Testeando wrappers"),
        ("process_document.py", "PASO 4/5: Procesando documento completo"),
        ("query.py", "PASO 5/5: Query de ejemplo"),
    ]
    
    for script, description in steps:
        run_script(script, description)
    
    print("\n" + "=" * 80)
    print("✓ PIPELINE COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print("\nAhora puedes:")
    print("  • Ejecutar queries: python 6_query.py --interactive")
    print("  • Ver el knowledge graph en: ./rag_storage")
    print("  • Ver documentos parseados en: ./output")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPipeline cancelado por el usuario")
        sys.exit(1)
