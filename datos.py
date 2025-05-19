import sqlite3

# Conectar a la base de datos (o crearla si no existe)
conn = sqlite3.connect("base.db")
cursor = conn.cursor()

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

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()