from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, send_from_directory, current_app
import os
from .db import get_db_connection
from .auth import autenticar

main_routes = Blueprint('main', __name__)

@main_routes.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        if autenticar(usuario, contrasena):
            session['usuario'] = usuario
            return redirect(url_for('main.principal'))
        return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

@main_routes.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('main.login'))

def requiere_login():
    return 'usuario' not in session

@main_routes.route('/principal')
def principal():
    if requiere_login():
        return redirect(url_for('main.login'))
    conn = get_db_connection()
    citas = conn.execute('SELECT * FROM citas').fetchall()
    conn.close()
    return render_template('pagPrincipal.html', citas=citas)

@main_routes.route('/buscar_pago', methods=['POST'])
def buscar_pago():
    nombre = request.form.get('nombre', '').strip()
    lote = request.form.get('lote', '').strip()
    manzana = request.form.get('manzana', '').strip()
    fraccionamiento = request.form.get('fraccionamiento', '').strip()

    query = "SELECT * FROM ventas WHERE 1=1"
    params = []

    if nombre:
        query += " AND nombre_cliente LIKE ?"
        params.append(f"%{nombre}%")
    if lote:
        query += " AND lote LIKE ?"
        params.append(f"%{lote}%")
    if manzana:
        query += " AND manzana LIKE ?"
        params.append(f"%{manzana}%")
    if fraccionamiento:
        query += " AND fraccionamiento LIKE ?"
        params.append(f"%{fraccionamiento}%")

    conn = get_db_connection()
    resultados = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('sanpedro.html', resultados=resultados)

@main_routes.route('/ventas')
def ventas():
    if requiere_login():
        return redirect(url_for('main.login'))
    conn = get_db_connection()
    ventas = conn.execute('SELECT * FROM ventas').fetchall()
    conn.close()
    return render_template('pagModuloVentas.html', ventas=ventas)

@main_routes.route('/ingresos')
def ingresos():
    if requiere_login():
        return redirect(url_for('main.login'))
    return render_template('pagModuloIngresoEgreso.html')

@main_routes.route('/mantenimiento')
def mantenimiento():
    if requiere_login():
        return redirect(url_for('main.login'))
    return render_template('pagModuloMantenimientoGasto.html')

@main_routes.route('/sanpedro')
def sanpedro():
    if requiere_login():
        return redirect(url_for('main.login'))
    return render_template('sanpedro.html')

@main_routes.route('/marcar_listo/<int:id>', methods=['POST'])
def eliminar_cita(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM citas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@main_routes.route('/modificar/<int:id>', methods=['POST'])
def modificar(id):
    data = request.json
    nueva_fecha = data.get('nueva_fecha')
    nueva_descripcion = data.get('nueva_descripcion')
    if nueva_fecha and nueva_descripcion:
        conn = get_db_connection()
        conn.execute('UPDATE citas SET fecha = ?, descripcion = ? WHERE id = ?',
                     (nueva_fecha, nueva_descripcion, id))
        conn.commit()
        conn.close()
        return jsonify(success=True)
    return jsonify(success=False, error="Datos inválidos"), 400

@main_routes.route('/agregar', methods=['POST'])
def agregar():
    data = request.json
    fecha = data.get('fecha')
    descripcion = data.get('descripcion')
    if fecha and descripcion:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO citas (fecha, descripcion) VALUES (?, ?)', (fecha, descripcion))
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()
        return jsonify(success=True, id=nuevo_id)
    return jsonify(success=False)

@main_routes.route('/registrar_pago', methods=['POST'])
def registrar_pago():
    data = request.get_json()

    campos = [
        'periodo', 'fecha', 'nombre_cliente', 'numero', 'lote', 'cantidad',
        'manzana', 'fraccionamiento', 'cerrador', 'agendador', 'comision',
        'pagado', 'venta_capturada', 'recibo', 'liquidacion', 'hora'
    ]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO ventas ({', '.join(campos)})
            VALUES ({', '.join(['?' for _ in campos])})
        """, [
            data.get('periodo'),
            data.get('fecha'),
            data.get('nombre_cliente'),
            data.get('numero', ''),  # Default si falta
            data.get('lote'),
            data.get('cantidad'),
            data.get('manzana'),
            data.get('fraccionamiento'),
            data.get('cerrador'),
            data.get('agendador'),
            data.get('comision'),
            data.get('pagado'),
            'CAPTURADO',  # Valor fijo como placeholder para 'venta_capturada'
            data.get('recibo'),
            data.get('liquidacion'),
            data.get('hora')
        ])
        conn.commit()
        conn.close()
        return jsonify(success=True)
    except Exception as e:
        print("Error al registrar pago:", e)
        return jsonify(success=False, error=str(e)), 500
