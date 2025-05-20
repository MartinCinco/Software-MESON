import sqlite3
import math
import pandas as pd

# Archivo Excel con datos
archivo_excel = 'clientes.xlsx'

# Leer el archivo Excel
df = pd.read_excel(archivo_excel)

# Columnas que esperamos en el Excel
columnas_esperadas = [
    'PERIODO', 'FECHA', 'NOMBRE_CLIENTE', 'NUMERO', 'LOTE',
    'CANTIDAD', 'MANZANA', 'FRACCIONAMIENTO', 'CERRADOR',
    'AGENDADOR', 'COMISION', 'PAGADO', 'VENTA_CAPTURADA',
    'RECIBO', 'LIQUIDACION', 'HORA'
]

df.columns = df.columns.str.strip().str.upper().str.replace(' ', '_')
if 'COMISIÓN' in df.columns:
    df.rename(columns={'COMISIÓN': 'COMISION'}, inplace=True)
print(df.columns.tolist())

# Verificar que el Excel tenga todas las columnas necesarias
if not all(col in df.columns for col in columnas_esperadas):
    missing = [col for col in columnas_esperadas if col not in df.columns]
    raise ValueError(f"El archivo Excel no contiene estas columnas: {missing}")

# Conexión a la base de datos SQLite
conn = sqlite3.connect('base.db')
cursor = conn.cursor()

errores = []

for index, fila in df.iterrows():
    try:
        valor_cantidad = fila['CANTIDAD']
        if valor_cantidad is None or (isinstance(valor_cantidad, float) and math.isnan(valor_cantidad)):
            raise ValueError("Cantidad es NaN o vacía")
        cantidad = int(float(valor_cantidad))
        if cantidad < 0:
            raise ValueError("Cantidad no puede ser negativa")

        comision = fila['COMISION']
        if comision is None or (isinstance(comision, float) and math.isnan(comision)):
            comision = ''  # valor por defecto para comisión
        else:
            comision = str(comision)

        cursor.execute('''
            INSERT INTO ventas (
                periodo, fecha, nombre_cliente, numero, lote, cantidad, manzana,
                fraccionamiento, cerrador, agendador, comision, pagado,
                venta_capturada, recibo, liquidacion, hora
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fila['PERIODO'], fila['FECHA'], fila['NOMBRE_CLIENTE'], fila['NUMERO'],
            fila['LOTE'], cantidad, fila['MANZANA'], fila['FRACCIONAMIENTO'],
            fila['CERRADOR'], fila['AGENDADOR'], comision, fila['PAGADO'],
            fila['VENTA_CAPTURADA'], fila['RECIBO'], fila['LIQUIDACION'], fila['HORA']
        ))

    except Exception as e:
        print(f"Error en fila {index + 2} (contando encabezado): valor cantidad = {valor_cantidad!r} -> {e}")


# Guardar cambios y cerrar conexión
conn.commit()
conn.close()
print(df.columns.tolist())

# Reportar resultados
#if errores:
#    print("Se encontraron errores en algunas filas:")
#    for idx, msg in errores:
 #       print(f"Fila {idx + 2} (considerando encabezado en fila 1): {msg}")
#else:
#    print("Todos los datos se cargaron correctamente.")