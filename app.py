from flask import Flask, render_template, request, redirect, url_for, jsonify, session

app = Flask(__name__)

# Lista de citas iniciales
citas = [
    {"fecha": "10/03/2025", "descripcion": "Revisión financiera"},
    {"fecha": "15/03/2025", "descripcion": "Pago de impuestos"},
    {"fecha": "20/03/2025", "descripcion": "Auditoría interna"}
]

app.secret_key = 'clave_secreta'

usuarios = {"admin": "1234"}  # Base de datos simulada

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
    return render_template('pagPrincipal.html')

@app.route('/ventas')
def ventas():
    return render_template('ventas.html')

@app.route('/ingresos')
def ingresos():
    return render_template('ventas.html')

@app.route('/mantenimiento')
def mantenimiento():
    return render_template('ventas.html')


@app.route('/marcar_listo/<int:index>', methods=['POST'])
def marcar_listo(index):
    if 0 <= index < len(citas):
        citas.pop(index)  # Elimina la cita
    return jsonify(success=True)

@app.route('/cancelar/<int:index>', methods=['POST'])
def cancelar(index):
    if 0 <= index < len(citas):
        citas.pop(index)  # Elimina la cita
    return jsonify(success=True)

@app.route('/modificar/<int:index>', methods=['POST'])
def modificar(index):
    try:
        data = request.json
        nueva_fecha = data.get('nueva_fecha')
        if 0 <= index < len(citas) and nueva_fecha:
            citas[index]['fecha'] = nueva_fecha
            return jsonify(success=True)
        return jsonify(success=False, error="Índice inválido o datos faltantes"), 400
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/agregar', methods=['POST'])
def agregar():
    data = request.json
    fecha = data.get('fecha')
    descripcion = data.get('descripcion')
    if fecha and descripcion:
        citas.append({"fecha": fecha, "descripcion": descripcion})
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
