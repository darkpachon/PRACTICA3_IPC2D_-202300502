import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib import messages
import json

def lista_productos(request):
    """Vista para listar todos los productos"""
    try:
        response = requests.get(f'{settings.FLASK_API_URL}/productos')
        if response.status_code == 200:
            productos = response.json()
        else:
            productos = []
            messages.error(request, 'Error al cargar los productos desde la API')
    except requests.exceptions.RequestException:
        productos = []
        messages.error(request, 'No se pudo conectar con la API de Flask')
    
    return render(request, 'inventario_app/lista_productos.html', {'productos': productos})

def detalle_producto(request, producto_id):
    """Vista para mostrar detalles de un producto específico"""
    try:
        response = requests.get(f'{settings.FLASK_API_URL}/productos/{producto_id}')
        if response.status_code == 200:
            producto = response.json()
            return render(request, 'inventario_app/detalle_producto.html', {'producto': producto})
        else:
            messages.error(request, 'Producto no encontrado')
            return redirect('lista_productos')
    except requests.exceptions.RequestException:
        messages.error(request, 'Error de conexión con la API')
        return redirect('lista_productos')

def crear_producto(request):
    """Vista para crear un nuevo producto"""
    if request.method == 'POST':
        try:
            data = {
                'nombre': request.POST.get('nombre'),
                'categoria': request.POST.get('categoria'),
                'descripcion': request.POST.get('descripcion'),
                'precio': float(request.POST.get('precio', 0)),
                'cantidad_en_stock': int(request.POST.get('cantidad_en_stock', 0)),
                'fecha_vencimiento': request.POST.get('fecha_vencimiento') or None
            }
            
            response = requests.post(
                f'{settings.FLASK_API_URL}/productos',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                messages.success(request, 'Producto creado exitosamente')
                return redirect('lista_productos')
            else:
                error_data = response.json()
                messages.error(request, f'Error al crear producto: {error_data.get("error", "Error desconocido")}')
                
        except ValueError as e:
            messages.error(request, 'Error en los datos: precio y cantidad deben ser números válidos')
        except requests.exceptions.RequestException:
            messages.error(request, 'Error de conexión con la API')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
    
    return render(request, 'inventario_app/crear_producto.html')

def editar_producto(request, producto_id):
    """Vista para editar un producto existente"""
    # Primero obtener el producto actual
    try:
        response = requests.get(f'{settings.FLASK_API_URL}/productos/{producto_id}')
        if response.status_code != 200:
            messages.error(request, 'Producto no encontrado')
            return redirect('lista_productos')
        
        producto = response.json()
        
    except requests.exceptions.RequestException:
        messages.error(request, 'Error de conexión con la API')
        return redirect('lista_productos')
    
    if request.method == 'POST':
        try:
            data = {
                'nombre': request.POST.get('nombre'),
                'categoria': request.POST.get('categoria'),
                'descripcion': request.POST.get('descripcion'),
                'precio': float(request.POST.get('precio', 0)),
                'cantidad_en_stock': int(request.POST.get('cantidad_en_stock', 0)),
                'fecha_vencimiento': request.POST.get('fecha_vencimiento') or None
            }
            
            response = requests.put(
                f'{settings.FLASK_API_URL}/productos/{producto_id}',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                messages.success(request, 'Producto actualizado exitosamente')
                return redirect('lista_productos')
            else:
                error_data = response.json()
                messages.error(request, f'Error al actualizar producto: {error_data.get("error", "Error desconocido")}')
                
        except ValueError as e:
            messages.error(request, 'Error en los datos: precio y cantidad deben ser números válidos')
        except requests.exceptions.RequestException:
            messages.error(request, 'Error de conexión con la API')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
    
    return render(request, 'inventario_app/editar_producto.html', {'producto': producto})

def eliminar_producto(request, producto_id):
    """Vista para eliminar un producto"""
    if request.method == 'POST':
        try:
            response = requests.delete(f'{settings.FLASK_API_URL}/productos/{producto_id}')
            
            if response.status_code == 200:
                messages.success(request, 'Producto eliminado exitosamente')
            else:
                error_data = response.json()
                messages.error(request, f'Error al eliminar producto: {error_data.get("error", "Error desconocido")}')
                
        except requests.exceptions.RequestException:
            messages.error(request, 'Error de conexión con la API')
    
    return redirect('lista_productos')