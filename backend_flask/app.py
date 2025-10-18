from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permitir requests desde Django

# Archivo JSON para almacenar los datos
INVENTARIO_FILE = 'inventario.json'

def cargar_inventario():
    """Cargar inventario desde archivo JSON"""
    if os.path.exists(INVENTARIO_FILE):
        with open(INVENTARIO_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def guardar_inventario(inventario):
    """Guardar inventario en archivo JSON"""
    with open(INVENTARIO_FILE, 'w', encoding='utf-8') as f:
        json.dump(inventario, f, indent=4, ensure_ascii=False)

def generar_id():
    """Generar un ID único para nuevo producto"""
    inventario = cargar_inventario()
    if not inventario:
        return 1
    return max(producto['id'] for producto in inventario) + 1

@app.route('/productos', methods=['GET'])
def obtener_productos():
    """Obtener todos los productos"""
    inventario = cargar_inventario()
    return jsonify(inventario)

@app.route('/productos/<int:producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    """Obtener un producto específico por ID"""
    inventario = cargar_inventario()
    producto = next((p for p in inventario if p['id'] == producto_id), None)
    
    if producto:
        return jsonify(producto)
    return jsonify({'error': 'Producto no encontrado'}), 404

@app.route('/productos', methods=['POST'])
def crear_producto():
    """Crear un nuevo producto"""
    try:
        data = request.get_json()
        
        # Validaciones
        campos_requeridos = ['nombre', 'categoria', 'descripcion', 'precio', 'cantidad_en_stock']
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                return jsonify({'error': f'El campo {campo} es requerido'}), 400
        
        # Validar tipos de datos
        try:
            precio = float(data['precio'])
            cantidad = int(data['cantidad_en_stock'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Precio y cantidad deben ser números válidos'}), 400
        
        if precio <= 0 or cantidad < 0:
            return jsonify({'error': 'Precio debe ser mayor a 0 y cantidad no puede ser negativa'}), 400
        
        nuevo_producto = {
            'id': generar_id(),
            'nombre': data['nombre'],
            'categoria': data['categoria'],
            'descripcion': data['descripcion'],
            'precio': precio,
            'cantidad_en_stock': cantidad,
            'fecha_vencimiento': data.get('fecha_vencimiento', None),
            'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        inventario = cargar_inventario()
        inventario.append(nuevo_producto)
        guardar_inventario(inventario)
        
        return jsonify(nuevo_producto), 201
        
    except Exception as e:
        return jsonify({'error': f'Error al crear producto: {str(e)}'}), 500

@app.route('/productos/<int:producto_id>', methods=['PUT'])
def actualizar_producto(producto_id):
    """Actualizar un producto existente"""
    try:
        data = request.get_json()
        inventario = cargar_inventario()
        
        producto_index = next((i for i, p in enumerate(inventario) if p['id'] == producto_id), None)
        
        if producto_index is None:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Validaciones
        if 'precio' in data:
            try:
                precio = float(data['precio'])
                if precio <= 0:
                    return jsonify({'error': 'El precio debe ser mayor a 0'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Precio debe ser un número válido'}), 400
        
        if 'cantidad_en_stock' in data:
            try:
                cantidad = int(data['cantidad_en_stock'])
                if cantidad < 0:
                    return jsonify({'error': 'La cantidad no puede ser negativa'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Cantidad debe ser un número entero válido'}), 400
        
        # Actualizar campos
        campos_actualizables = ['nombre', 'categoria', 'descripcion', 'precio', 'cantidad_en_stock', 'fecha_vencimiento']
        for campo in campos_actualizables:
            if campo in data:
                inventario[producto_index][campo] = data[campo]
        
        inventario[producto_index]['fecha_actualizacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        guardar_inventario(inventario)
        
        return jsonify(inventario[producto_index])
        
    except Exception as e:
        return jsonify({'error': f'Error al actualizar producto: {str(e)}'}), 500

@app.route('/productos/<int:producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    """Eliminar un producto"""
    inventario = cargar_inventario()
    producto_index = next((i for i, p in enumerate(inventario) if p['id'] == producto_id), None)
    
    if producto_index is None:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    producto_eliminado = inventario.pop(producto_index)
    guardar_inventario(inventario)
    
    return jsonify({'mensaje': 'Producto eliminado correctamente', 'producto': producto_eliminado})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Inicializar archivo JSON si no existe
    if not os.path.exists(INVENTARIO_FILE):
        guardar_inventario([])
    
    app.run(debug=True, port=5000)