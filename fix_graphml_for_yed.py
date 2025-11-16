#!/usr/bin/env python3
"""
Script para añadir etiquetas compatibles con yEd usando namespace yFiles
"""

import xml.etree.ElementTree as ET
from pathlib import Path

def fix_graphml_for_yed(input_file: str, output_file: str = None):
    """
    Añade labels compatibles con yEd usando el namespace y: (yFiles)
    """
    if output_file is None:
        output_file = input_file
    
    # Parsear el XML
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # Namespaces
    ns = {'graphml': 'http://graphml.graphdrawing.org/xmlns'}
    y_ns = 'http://www.yworks.com/xml/graphml'
    
    # Registrar namespaces
    ET.register_namespace('', 'http://graphml.graphdrawing.org/xmlns')
    ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    ET.register_namespace('y', y_ns)
    
    # Verificar si ya existe key para NodeLabel
    keys = root.findall('graphml:key', ns)
    node_graphics_exists = any(k.get('id') == 'd_nodegraphics' for k in keys)
    
    if not node_graphics_exists:
        # Añadir key para NodeLabel (antes del graph)
        node_key = ET.Element('key', {
            'id': 'd_nodegraphics',
            'for': 'node',
            'yfiles.type': 'nodegraphics'
        })
        
        # Insertar después del último key
        last_key_idx = max([i for i, elem in enumerate(root) if elem.tag.endswith('key')], default=-1)
        root.insert(last_key_idx + 1, node_key)
        print("✓ Añadida key para nodegraphics")
    
    # Procesar cada nodo
    nodes_updated = 0
    for node in root.findall('.//graphml:node', ns):
        node_id = node.get('id')
        
        # Buscar el entity_id (key d0)
        entity_id_elem = node.find("graphml:data[@key='d0']", ns)
        
        if entity_id_elem is not None and entity_id_elem.text:
            entity_id = entity_id_elem.text
            
            # Verificar si ya tiene ShapeNode
            graphics_elem = node.find("graphml:data[@key='d_nodegraphics']", ns)
            
            if graphics_elem is None:
                # Crear elemento de gráficos yFiles
                graphics_elem = ET.SubElement(node, '{http://graphml.graphdrawing.org/xmlns}data', 
                                              {'key': 'd_nodegraphics'})
                
                # Crear ShapeNode
                shape_node = ET.SubElement(graphics_elem, f'{{{y_ns}}}ShapeNode')
                
                # Geometry (tamaño del nodo)
                geometry = ET.SubElement(shape_node, f'{{{y_ns}}}Geometry', {
                    'height': '30.0',
                    'width': str(max(80.0, len(entity_id) * 8.0)),
                    'x': '0.0',
                    'y': '0.0'
                })
                
                # Fill (color de relleno)
                fill = ET.SubElement(shape_node, f'{{{y_ns}}}Fill', {
                    'color': '#E8EAF6',
                    'transparent': 'false'
                })
                
                # BorderStyle
                border = ET.SubElement(shape_node, f'{{{y_ns}}}BorderStyle', {
                    'color': '#3F51B5',
                    'type': 'line',
                    'width': '1.0'
                })
                
                # NodeLabel con el texto
                label = ET.SubElement(shape_node, f'{{{y_ns}}}NodeLabel', {
                    'alignment': 'center',
                    'autoSizePolicy': 'content',
                    'fontFamily': 'Dialog',
                    'fontSize': '12',
                    'fontStyle': 'plain',
                    'hasBackgroundColor': 'false',
                    'hasLineColor': 'false',
                    'height': '18.0',
                    'horizontalTextPosition': 'center',
                    'iconTextGap': '4',
                    'modelName': 'custom',
                    'textColor': '#000000',
                    'verticalTextPosition': 'bottom',
                    'visible': 'true',
                    'width': str(max(60.0, len(entity_id) * 7.0)),
                    'x': '0.0',
                    'y': '6.0'
                })
                label.text = entity_id
                
                # Shape
                shape = ET.SubElement(shape_node, f'{{{y_ns}}}Shape', {
                    'type': 'roundrectangle'
                })
                
                nodes_updated += 1
            else:
                # Ya tiene gráficos, actualizar solo el label
                label_elem = graphics_elem.find(f".//{{{y_ns}}}NodeLabel", {})
                if label_elem is not None:
                    label_elem.text = entity_id
                    nodes_updated += 1
    
    print(f"✓ Añadidos gráficos yEd a {nodes_updated} nodos")
    
    # Guardar
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"✓ Archivo guardado en: {output_file}")
    
    return nodes_updated


if __name__ == "__main__":
    import sys
    
    default_path = "./storage/rag_storage/graph_chunk_entity_relation.graphml"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        input_file = default_path
        output_file = None
    
    if not Path(input_file).exists():
        print(f"✗ Error: No se encuentra el archivo {input_file}")
        sys.exit(1)
    
    print(f"Procesando: {input_file}")
    print("=" * 60)
    
    try:
        fix_graphml_for_yed(input_file, output_file)
        print("=" * 60)
        print("✓ ¡Listo! Recarga el archivo en yEd")
        print("  Nota: Los nodos tendrán formato básico, puedes aplicar")
        print("        estilos adicionales desde yEd después")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

