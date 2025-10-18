from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
import requests
from .forms import ProductForm

API_BASE = "http://127.0.0.1:5000"

def product_list(request):
    try:
        r = requests.get(f"{API_BASE}/productos", timeout=5)
        r.raise_for_status()
        productos = r.json()
    except Exception as e:
        productos = []
        messages.error(request, f"No se pudo conectar con la API: {e}")
    return render(request, "inventory_client/product_list.html", {"productos": productos})

def product_detail(request, prod_id):
    try:
        r = requests.get(f"{API_BASE}/productos/{prod_id}", timeout=5)
        if r.status_code == 404:
            messages.error(request, "Producto no encontrado.")
            return redirect("inventory_client:product_list")
        r.raise_for_status()
        producto = r.json()
    except Exception as e:
        messages.error(request, f"Error al obtener producto: {e}")
        return redirect("inventory_client:product_list")
    return render(request, "inventory_client/product_detail.html", {"p": producto})

def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            payload = form.cleaned_data
            try:
                r = requests.post(f"{API_BASE}/productos", json=payload, timeout=5)
                r.raise_for_status()
                messages.success(request, "Producto creado correctamente.")
                return redirect("inventory_client:product_list")
            except Exception as e:
                messages.error(request, f"Error al crear producto: {e}")
    else:
        form = ProductForm()
    return render(request, "inventory_client/product_form.html", {"form": form, "action": "Crear"})

def product_edit(request, prod_id):
    try:
        r = requests.get(f"{API_BASE}/productos/{prod_id}", timeout=5)
        if r.status_code == 404:
            messages.error(request, "Producto no encontrado.")
            return redirect("inventory_client:product_list")
        r.raise_for_status()
        producto = r.json()
    except Exception as e:
        messages.error(request, f"Error al obtener producto: {e}")
        return redirect("inventory_client:product_list")

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            payload = form.cleaned_data
            try:
                r = requests.put(f"{API_BASE}/productos/{prod_id}", json=payload, timeout=5)
                r.raise_for_status()
                messages.success(request, "Producto actualizado.")
                return redirect("inventory_client:product_detail", prod_id=prod_id)
            except Exception as e:
                messages.error(request, f"Error al actualizar producto: {e}")
    else:
        initial = {
            "nombre": producto.get("nombre"),
            "categoria": producto.get("categoria"),
            "descripcion": producto.get("descripcion"),
            "precio": producto.get("precio"),
            "cantidad": producto.get("cantidad"),
            "fecha_vencimiento": producto.get("fecha_vencimiento"),
        }
        form = ProductForm(initial=initial)
    return render(request, "inventory_client/product_form.html", {"form": form, "action": "Editar", "prod_id": prod_id})

def product_delete(request, prod_id):
    if request.method == "POST":
        try:
            r = requests.delete(f"{API_BASE}/productos/{prod_id}", timeout=5)
            if r.status_code == 404:
                messages.error(request, "Producto no encontrado.")
            else:
                r.raise_for_status()
                messages.success(request, "Producto eliminado.")
        except Exception as e:
            messages.error(request, f"Error al eliminar: {e}")
        return redirect("inventory_client:product_list")
    else:
        try:
            r = requests.get(f"{API_BASE}/productos/{prod_id}", timeout=5)
            r.raise_for_status()
            producto = r.json()
        except Exception as e:
            messages.error(request, f"Error al obtener producto: {e}")
            return redirect("inventory_client:product_list")
        return render(request, "inventory_client/product_confirm_delete.html", {"p": producto})
