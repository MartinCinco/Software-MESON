import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans, DBSCAN
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import os

escritorio = os.path.join(os.path.expanduser("~"), "Desktop")

def ejecutar_segmentacion(filtros):
    # Crear carpeta de resultados si no existe
    if not os.path.exists(escritorio+"/resultados"):
        os.makedirs(escritorio+"/resultados")

    # Cargar datos
    df = pd.read_excel("recursos/clientes.xlsx")
    df.columns = df.columns.str.strip()
    
    # Preparar columnas necesarias
    df['comisión'] = pd.to_numeric(
        df['COMISIÓN'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip(),
        errors='coerce'
    )
    df['estatus_pago'] = df['PAGADO'].apply(lambda x: 1 if x == 'PAGADO' else (0 if x == 'CANCELO' else 2))
    df['estatus_liquidacion'] = df['LIQUIDACION'].apply(lambda x: 1 if x == 'LIQUIDADO' else (0 if x == 'CANCELO' else 2))
    df['FRACCIONAMIENTO'] = df['FRACCIONAMIENTO'].str.strip().str.replace(r'\s*\d+$', '', regex=True)
    df['fraccionamiento'] = df['FRACCIONAMIENTO'].astype('category').cat.codes
    df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')
    df['recencia_dias'] = (pd.Timestamp.today() - df['FECHA']).dt.days
    df['frecuencia_visita'] = df.groupby('NOMBRE CLIENTE')['FECHA'].transform('count')

    # Aplicar filtros
    if filtros['cliente']:
        df = df[df['NOMBRE CLIENTE'].str.contains(filtros['cliente'], case=False)]
    if filtros['fraccionamiento']:
        df = df[df['FRACCIONAMIENTO'].str.contains(filtros['fraccionamiento'], case=False)]
    if filtros['fecha_min']:
        df = df[df['FECHA'] >= pd.to_datetime(filtros['fecha_min'])]
    if filtros['fecha_max']:
        df = df[df['FECHA'] <= pd.to_datetime(filtros['fecha_max'])]

    # Agrupar por cliente
    clientes = df.groupby('NOMBRE CLIENTE').agg({
        'comisión': 'sum',
        'estatus_pago': 'mean',
        'estatus_liquidacion': 'mean',
        'CANTIDAD': 'sum',
        'fraccionamiento': 'mean',
        'recencia_dias': 'min'
    }).reset_index()

    # Añadir fraccionamiento original (nombre)
    df_fracc = df[['NOMBRE CLIENTE', 'FRACCIONAMIENTO']].drop_duplicates()
    clientes = clientes.merge(df_fracc, on='NOMBRE CLIENTE', how='left')
    clientes = clientes.rename(columns={'FRACCIONAMIENTO': 'nombre_fraccionamiento'})

    # Selección de variables
    columnas_disponibles = {
        'comision': 'comisión',
        'cantidad': 'CANTIDAD',
        'recencia_dias': 'recencia_dias',
        'estatus_pago': 'estatus_pago',
        'estatus_liquidacion': 'estatus_liquidacion',
        'fraccionamiento': 'fraccionamiento'
    }
    variables_usar = [columnas_disponibles[var] for var in filtros['variables'] if var in columnas_disponibles]

    preprocessor = ColumnTransformer([
        ('seleccionadas', StandardScaler(), variables_usar)
    ])

    X = preprocessor.fit_transform(clientes)

    imputer = SimpleImputer(strategy='mean')
    X_imputed = imputer.fit_transform(X)

    # Aplicar algoritmo de clustering
    if filtros['algoritmo'] == 'kmeans':
        model = KMeans(n_clusters=filtros['num_clusters'], random_state=42)
        clientes['cluster'] = model.fit_predict(X_imputed)
    elif filtros['algoritmo'] == 'dbscan':
        model = DBSCAN(eps=1.0, min_samples=5)
        clientes['cluster'] = model.fit_predict(X_imputed)
    else:
        raise ValueError("Algoritmo no reconocido")

    # Guardar resultados
    if filtros['exportar_csv']:
        clientes.to_csv(escritorio+"/resultados/clientes_segmentados.csv", index=False)

    if filtros['exportar_pdf']:
        with PdfPages(escritorio+"/resultados/reporte_segmentacion.pdf") as pdf:
            plt.figure()
            plt.scatter(clientes['comisión'], clientes['recencia_dias'], c=clientes['cluster'], cmap='viridis')
            plt.xlabel("Comisión")
            plt.ylabel("Recencia")
            plt.title(f"Clusters de clientes - {filtros['algoritmo'].upper()}")
            pdf.savefig()
            plt.close()

            plt.figure()
            conteo = clientes.groupby(['cluster', 'nombre_fraccionamiento']).size().unstack(fill_value=0)
            conteo.plot(kind='bar', stacked=True, figsize=(10,6))
            plt.title("Distribución por fraccionamiento y cluster")
            plt.tight_layout()
            pdf.savefig()
            plt.close()

    print("Segmentación ejecutada y archivos generados.")
