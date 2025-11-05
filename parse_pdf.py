import subprocess
import os
import json
from config import PDF_PATH, PARSED_OUTPUT, MINERU_PARSE_METHOD, MINERU_LANG, DEVICE

def parse_pdf_with_mineru():
    """
    Parsea el PDF usando MinerU directamente desde línea de comandos
    """
    
    print("=== FASE 2: Parseando PDF con MinerU ===")
    print(f"Documento: {PDF_PATH}")
    print(f"Output: {PARSED_OUTPUT}")
    print(f"Método: {MINERU_PARSE_METHOD}")
    print(f"Device: {DEVICE}")
    
    # Verificar que el PDF existe
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF no encontrado: {PDF_PATH}")
    
    # Comando MinerU
    cmd = [
        "mineru",
        "-p", PDF_PATH,
        "-o", PARSED_OUTPUT,
        "-m", MINERU_PARSE_METHOD,
        "--device", DEVICE,
        "--lang", MINERU_LANG
    ]
    
    print(f"\nEjecutando: {' '.join(cmd)}\n")
    
    # Ejecutar MinerU
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Mostrar siempre stdout y stderr
    if result.stdout:
        print("\nstdout:")
        print(result.stdout)
    if result.stderr:
        print("\nstderr:")
        print(result.stderr)
    
    if result.returncode != 0:
        raise RuntimeError(f"MinerU falló con código {result.returncode}")
    
    # Verificar que se generó contenido
    output_files = []
    for root, dirs, files in os.walk(PARSED_OUTPUT):
        output_files.extend(files)
    
    if not output_files:
        raise RuntimeError("MinerU no generó ningún archivo de salida. Posible error silencioso.")
    
    print("\n=== Parsing completado ===")
    print(f"Archivos generados: {len(output_files)}")
    
    # Verificar output
    print("\n=== Estructura del output ===")
    for root, dirs, files in os.walk(PARSED_OUTPUT):
        level = root.replace(PARSED_OUTPUT, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files[:10]:  # Mostrar solo los primeros 10 archivos
            print(f'{subindent}{file}')
        if len(files) > 10:
            print(f'{subindent}... y {len(files) - 10} archivos más')

if __name__ == "__main__":
    parse_pdf_with_mineru()
