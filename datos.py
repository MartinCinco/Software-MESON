import sqlite3

# Conectar a la base de datos (la crea si no existe)
conn = sqlite3.connect('base.db')
cursor = conn.cursor()

# Crear tablas
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    contrasena TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS citas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    descripcion TEXT NOT NULL
)
''')

# Insertar datos
cursor.execute("INSERT OR IGNORE INTO usuarios (usuario, contrasena) VALUES (?, ?)", ('admin', '1234'))
cursor.execute("INSERT INTO citas (fecha, descripcion) VALUES (?, ?)", ('2025-05-15', 'Primera cita de prueba'))

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()
