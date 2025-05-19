import sqlite3

# Conectar a la base de datos (o crearla si no existe)
conn = sqlite3.connect("base.db")
cursor = conn.cursor()

# Crear tabla usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL,
    contrasena TEXT NOT NULL
)
''')

# Crear tabla citas
cursor.execute('''
CREATE TABLE IF NOT EXISTS citas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    descripcion TEXT
)
''')

# Crear tabla 'ventas'
cursor.execute("""
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    periodo TEXT,
    fecha TEXT,
    nombre_cliente TEXT,
    numero TEXT,
    lote TEXT,
    cantidad INTEGER,
    manzana TEXT,
    fraccionamiento TEXT,
    cerrador TEXT,
    agendador TEXT,
    comision TEXT,
    pagado TEXT,
    venta_capturada TEXT,
    recibo TEXT,
    liquidacion TEXT,
    hora TEXT
);
""")

# Insertar usuario admin
cursor.execute('''
INSERT INTO usuarios (usuario, contrasena)
VALUES (?, ?)
''', ('admin', '1234'))

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()