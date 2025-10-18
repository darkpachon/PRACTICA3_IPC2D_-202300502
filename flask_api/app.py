from flask import Flask, jsonify, request, abort
import json
import threading
import uuid
from pathlib import Path

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "inventario.json"
lock = threading.Lock()

def read_data():
    with lock:
        if not DATA_FILE.exists():
            DATA_FILE.write_text("[]", encoding="utf-8")
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data

def write_data(data):
    with lock:
        DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def find_product(data, prod_id):
    for p in data:
        if str(p.get("id")) == str(prod_id):
            return p
    return None

@app.route("/productos", methods=["GET"])
def list_products():
    data = read_data()
    return jsonify(data), 200

@app.route("/productos/<prod_id>", methods=["GET"])
def get_product(prod_id):
    data = read_data()
    p = find_product(data, prod_id)
    if not p:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(p), 200

@app.route("/productos", methods=["POST"])
def create_product():
    if not request.is_json:
        return jsonify({"error": "Se espera JSON"}), 400
    body = request.get_json()
    # validaciones básicas
    required = ["nombre", "categoria", "precio", "cantidad"]
    for r in required:
        if r not in body:
            return jsonify({"error": f"Falta campo {r}"}), 400
    try:
        precio = float(body["precio"])
        cantidad = int(body["cantidad"])
    except ValueError:
        return jsonify({"error": "precio debe ser número y cantidad entero"}), 400

    new = {
        "id": str(uuid.uuid4()),
        "nombre": body.get("nombre"),
        "categoria": body.get("categoria"),
        "descripcion": body.get("descripcion", ""),
        "precio": precio,
        "cantidad": cantidad,
        "fecha_vencimiento": body.get("fecha_vencimiento")
    }
    data = read_data()
    data.append(new)
    write_data(data)
    return jsonify(new), 201

@app.route("/productos/<prod_id>", methods=["PUT"])
def update_product(prod_id):
    if not request.is_json:
        return jsonify({"error": "Se espera JSON"}), 400
    body = request.get_json()
    data = read_data()
    p = find_product(data, prod_id)
    if not p:
        return jsonify({"error": "Producto no encontrado"}), 404

    for k in ["nombre", "categoria", "descripcion", "precio", "cantidad", "fecha_vencimiento"]:
        if k in body:
            if k == "precio":
                try:
                    p[k] = float(body[k])
                except:
                    return jsonify({"error": "precio debe ser numérico"}), 400
            elif k == "cantidad":
                try:
                    p[k] = int(body[k])
                except:
                    return jsonify({"error": "cantidad debe ser entero"}), 400
            else:
                p[k] = body[k]
    write_data(data)
    return jsonify(p), 200

@app.route("/productos/<prod_id>", methods=["DELETE"])
def delete_product(prod_id):
    data = read_data()
    p = find_product(data, prod_id)
    if not p:
        return jsonify({"error": "Producto no encontrado"}), 404
    data = [x for x in data if str(x.get("id")) != str(prod_id)]
    write_data(data)
    return jsonify({"message": "Producto eliminado"}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Recurso no encontrado"}), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
