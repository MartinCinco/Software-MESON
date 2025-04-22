import threading
import webview
from flask import Flask, render_template, request, redirect, url_for, jsonify, session

app = Flask(__name__)

# Lista de citas iniciales
next_id = 4
citas = [
    {"id": 1, "fecha": "10/03/2025", "descripcion": "Revisión financiera"},
    {"id": 2, "fecha": "15/03/2025", "descripcion": "Pago de impuestos"},
    {"id": 3, "fecha": "20/03/2025", "descripcion": "Auditoría interna"}
]

app.secret_key = 'clave_secreta'

usuarios = {"admin": "1234"}  # Base de datos simulada

def start_flask():
    app.run(port=5000)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        if usuario in usuarios and usuarios[usuario] == contrasena:
            session['usuario'] = usuario
            return redirect(url_for('principal'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/principal')
def principal():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Evita acceso sin autenticación
    return render_template('pagPrincipal.html', citas=citas)

@app.route('/ventas')
def ventas():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Evita acceso sin autenticación
    return render_template('pagModuloVentas.html')

@app.route('/ingresos')
def ingresos():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Evita acceso sin autenticación
    return render_template('pagModuloIngresoEgreso.html')

@app.route('/mantenimiento')
def mantenimiento():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Evita acceso sin autenticación
    return render_template('pagModuloMantenimientoGasto.html')


@app.route('/cancelar/<int:id>', methods=['POST'])
def cancelar(id):
    global citas
    cita = next((c for c in citas if c["id"] == id), None)
    if cita:
        citas.remove(cita)
        return jsonify(success=True)
    return jsonify(success=False, error="Cita no encontrada"), 404

@app.route('/marcar_listo/<int:id>', methods=['POST'])
def marcar_listo(id):
    global citas
    cita = next((c for c in citas if c["id"] == id), None)
    if cita:
        citas.remove(cita)
        return jsonify(success=True)
    return jsonify(success=False, error="Cita no encontrada"), 404

@app.route('/modificar/<int:id>', methods=['POST'])
def modificar(id):
    try:
        data = request.json
        nueva_fecha = data.get('nueva_fecha')
        nueva_descripcion = data.get('nueva_descripcion')
        cita = next((c for c in citas if c["id"] == id), None)
        if cita and nueva_fecha and nueva_descripcion:
            cita['fecha'] = nueva_fecha
            cita['descripcion'] = nueva_descripcion
            return jsonify(success=True)
        return jsonify(success=False, error="Datos inválidos o cita no encontrada"), 400
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/agregar', methods=['POST'])
def agregar():
    global next_id, citas
    data = request.json
    fecha = data.get('fecha')
    descripcion = data.get('descripcion')
    if fecha and descripcion:
        nueva_cita = {"id": next_id, "fecha": fecha, "descripcion": descripcion}
        citas.append(nueva_cita)
        next_id += 1
        return jsonify(success=True, id=nueva_cita["id"])
    return jsonify(success=False)


if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    import time
    time.sleep(2)  # espera mínima para asegurar que Flask arranque

    print("Lanzando ventana...")
    webview.create_window("Mi App Escritorio", "http://127.0.0.1:5000")
    webview.start(debug=True)
