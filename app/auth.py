from .db import get_db_connection

def autenticar(usuario, contrasena):
    conn = get_db_connection()
    cursor = conn.execute(
        'SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?',
        (usuario, contrasena)
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None