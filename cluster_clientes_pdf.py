import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from kmodes.kprototypes import KPrototypes
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

# ===============================
# FUNCIONES DE PROCESAMIENTO
# ===============================

def limpiar_datos(df):
    df['COMISIÓN'] = df['COMISIÓN'].replace('[\$,]', '', regex=True).str.replace('.', '').str.replace(',', '.').astype(float)

    df['NUM_LOTES'] = df['LOTE'].astype(str).apply(lambda x: len(str(x).split(',')))
    
    df['PAGADO'] = df['PAGADO'].str.strip().str.upper().map(lambda x: 1 if x == 'PAGADO' else 0)
    df['CAPTURADO'] = df['VENTA CAPTURADA'].str.strip().str.upper().map(lambda x: 1 if x == 'CAPTURADO' else 0)
    df['LIQUIDACION'] = df['LIQUIDACION'].str.strip().str.upper().map(lambda x: 1 if x == 'LIQUIDO' else 0)

    columnas = ['NUM_LOTES', 'MANZANA', 'COMISIÓN', 'FRACCIONAMIENTO', 'CERRADOR', 'AGENDADOR', 'PAGADO', 'CAPTURADO', 'LIQUIDACION']
    df_limpio = df[columnas].copy()

    df_limpio.fillna('DESCONOCIDO', inplace=True)
    return df_limpio

def crear_graficos(df):
    os.makedirs("graficos", exist_ok=True)

    plt.figure(figsize=(6,4))
    sns.countplot(x='CLUSTER', data=df)
    plt.title("Distribución de Clientes por Clúster")
    plt.savefig("graficos/cluster_distribucion.png")
    plt.close()

    plt.figure(figsize=(6,4))
    sns.boxplot(x='CLUSTER', y='COMISIÓN', data=df)
    plt.title("Comisión por Clúster")
    plt.savefig("graficos/comision_cluster.png")
    plt.close()

    plt.figure(figsize=(6,4))
    sns.boxplot(x='CLUSTER', y='NUM_LOTES', data=df)
    plt.title("Número de Lotes por Clúster")
    plt.savefig("graficos/lotes_cluster.png")
    plt.close()

def generar_pdf(df, nombre_pdf="reporte_clientes.pdf"):
    c = canvas.Canvas(nombre_pdf, pagesize=letter)
    c.setFont("Helvetica", 14)
    c.drawString(50, 760, "Reporte de Clústeres de Clientes")

    # Resumen por clúster
    resumen = df.groupby('CLUSTER')[['NUM_LOTES', 'COMISIÓN', 'PAGADO', 'LIQUIDACION']].mean().round(2)
    c.setFont("Helvetica", 10)
    y = 730
    for i, row in resumen.iterrows():
        c.drawString(50, y, f"Clúster {i}: Lotes Prom: {row['NUM_LOTES']} | Comisión Prom: ${row['COMISIÓN']} | Pagado: {row['PAGADO']} | Liquidado: {row['LIQUIDACION']}")
        y -= 15

    # Insertar imágenes de gráficos
    graficos = ["graficos/cluster_distribucion.png", "graficos/comision_cluster.png", "graficos/lotes_cluster.png"]
    y = 600
    for grafico in graficos:
        c.drawImage(ImageReader(grafico), 50, y, width=500, height=150)
        y -= 170

    c.save()

# ===============================
# EJECUCIÓN PRINCIPAL
# ===============================

archivo = 'clientes.xlsx'  # Cambia según tu archivo
df = pd.read_excel(archivo)
df_limpio = limpiar_datos(df)

# Matriz y categorías
matriz = df_limpio.values
categorical_cols = [3, 4, 5]  # FRACCIONAMIENTO, CERRADOR, AGENDADOR

# Clustering
kproto = KPrototypes(n_clusters=3, init='Cao', verbose=0)
clusters = kproto.fit_predict(matriz, categorical=categorical_cols)
df['CLUSTER'] = clusters

# Guardar Excel
df.to_excel('clientes_clasificados.xlsx', index=False)

# Crear gráficos y PDF
crear_graficos(df)
generar_pdf(df)

print("✔ Clustering realizado.")
print("📊 Gráficos guardados en carpeta 'graficos'")
print("📄 PDF generado como 'reporte_clientes.pdf'")
