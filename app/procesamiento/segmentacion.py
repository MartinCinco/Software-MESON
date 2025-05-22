# 📦 Librerías estándar
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# 📊 Visualización
import seaborn as sns

# 🧪 Estadística
import scipy.stats as stats

# ⚙️ Preprocesamiento
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# 📈 Modelado y Clustering
from sklearn.cluster import KMeans, DBSCAN
from sklearn.linear_model import LogisticRegression

# 📊 Evaluación de modelos
from sklearn.model_selection import train_test_split
from sklearn.metrics import (classification_report,
    silhouette_score,roc_auc_score,f1_score)

from IPython.display import display

import os

escritorio = os.path.join(os.path.expanduser("~"), "Desktop")

# Cargar datos
df = pd.read_excel("clientes.xlsx")

df.columns = df.columns.str.strip()

df['comisión'] = pd.to_numeric(
    df['COMISIÓN'].astype(str)
    .str.replace('$', '', regex=False)
    .str.replace(',', '', regex=False)
    .str.strip(),
    errors='coerce'
)
df['estatus_pago'] = df['PAGADO'].apply(lambda x: 1 if x == 'PAGADO' else (0 if x == 'CANCELO' else 2))
df['FRACCIONAMIENTO'] = df['FRACCIONAMIENTO'].str.strip()
df['FRACCIONAMIENTO'] = df['FRACCIONAMIENTO'].str.replace(r'\s*\d+$', '', regex=True)
df['fraccionamiento'] = df['FRACCIONAMIENTO'].astype('category').cat.codes
df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')
df['recencia_dias'] = (pd.Timestamp.today() - df['FECHA']).dt.days
df['estatus_liquidacion'] = df['LIQUIDACION'].apply(lambda x: 1 if x == 'LIQUIDADO' else (0 if x == 'CANCELO' else 2))
df['frecuencia_visita'] = df.groupby('NOMBRE CLIENTE')['FECHA'].transform('count')

# Agrupar por cliente
clientes = df.groupby('NOMBRE CLIENTE').agg({
    'comisión': 'sum',
    'estatus_pago': 'mean',
    'estatus_liquidacion': 'mean',
    'CANTIDAD': 'sum',
    'fraccionamiento': 'mean',
    'recencia_dias': 'min'
}).reset_index()

preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(), ['comisión', 'CANTIDAD', 'recencia_dias']),
    ('ord', 'passthrough', ['estatus_pago', 'estatus_liquidacion']),
    ('cat', 'passthrough', ['fraccionamiento'])
])

X_final = preprocessor.fit_transform(clientes)

# Escalar datos
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X_final)

# Clustering
kmeans = KMeans(n_clusters=3, random_state=42)
clientes['cluster'] = kmeans.fit_predict(X_imputed)

# Seleccionar solo columnas numéricas
num_cols = clientes.select_dtypes(include=['number'])

# Agrupar y contar clientes por cluster y fraccionamiento
conteo = clientes.groupby(['cluster', 'fraccionamiento']).size().unstack(fill_value=0)

clientes.groupby('cluster')['estatus_pago'].describe()

# Método del codo
distorsiones = []
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_imputed)
    distorsiones.append(kmeans.inertia_)

# Silhouette
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k, random_state=42)
    preds = kmeans.fit_predict(X_imputed)
    score = silhouette_score(X_imputed, preds)
    print(f'k={k} → Silhouette={score:.3f}')

# DBSCAN: clustering basado en densidad
# Aplicar DBSCAN
dbscan = DBSCAN(eps=1.0, min_samples=5)
clientes['cluster_dbscan'] = dbscan.fit_predict(X_imputed)

resumen = clientes.groupby('cluster_dbscan').agg({
    'comisión': ['mean', 'min', 'max'],
    'CANTIDAD': ['mean'],
    'recencia_dias': ['mean'],
    'estatus_pago': ['mean'],
    'estatus_liquidacion': ['mean']
})

# Aplanar columnas para facilitar visualización
resumen.columns = ['_'.join(col) for col in resumen.columns]
resumen.reset_index(inplace=True)

perfiles = {
    -1: "Premium/Excepcional",
     0: "Típico con pagos en proceso",
     1: "Cancelado",
     2: "Cancelado antiguo",
     3: "Indefinido sin contacto",
     4: "Pagador sin liquidar",
     5: "Valioso sin seguimiento"
}
clientes['perfil'] = clientes['cluster_dbscan'].map(perfiles)
clientes.to_csv(os.path.join(escritorio, "clientes_segmentados_dbscan.csv"), index=False)

clientes['retencion'] = clientes['recencia_dias'].apply(lambda x: 1 if x < 360 else 0)
y = clientes['retencion']  # Asegúrate de que esta columna existe
X_train, X_test, y_train, y_test = train_test_split(X_imputed, y, test_size=0.3, random_state=42)
model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

umbrales = list(range(30, 361, 15))  # de 30 a 360 días
resultados = []

for u in umbrales:
    clientes['retencion_tmp'] = clientes['recencia_dias'].apply(lambda x: 1 if x < u else 0)
    y_tmp = clientes['retencion_tmp']

    if y_tmp.nunique() < 2:
        continue  # saltar si solo hay una clase

    X_train, X_test, y_train, y_test = train_test_split(
        X_imputed, y_tmp, test_size=0.3, random_state=42, stratify=y_tmp
    )

    model = LogisticRegression(class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    auc = roc_auc_score(y_test, y_prob)
    f1 = f1_score(y_test, y_pred)

    resultados.append((u, auc, f1))

# Visualizar resultados
resultados_df = pd.DataFrame(resultados, columns=['umbral', 'auc', 'f1'])

# Mejor umbral
mejor = resultados_df.sort_values(by='f1', ascending=False).iloc[0]

ruta_pdf = os.path.join(escritorio, "reporte_graficas_clientes.pdf")
with PdfPages(ruta_pdf) as pdf:

    # Gráfico 1: Scatterplot K-Means
    plt.figure()
    plt.scatter(clientes['comisión'], clientes['recencia_dias'], c=clientes['cluster'])
    plt.xlabel('Comisión Total')
    plt.ylabel('Recencia (días)')
    plt.title('Clusters de Clientes (K-Means)')
    pdf.savefig()
    plt.close()

    # Gráfico 2: Matriz de correlación
    plt.figure()
    sns.heatmap(num_cols.corr(), annot=True, cmap='coolwarm')
    plt.title("Matriz de Correlación")
    pdf.savefig()
    plt.close()

    # Gráfico 3: Barras apiladas por fraccionamiento
    plt.figure()
    conteo.plot(kind='bar', stacked=True, figsize=(12,6))
    plt.title('Distribución de clientes por fraccionamiento y cluster')
    plt.xlabel('Cluster')
    plt.ylabel('Cantidad de clientes')
    plt.tight_layout()
    pdf.savefig()
    plt.close()

    # Gráfico 4: Método del Codo
    plt.figure()
    plt.plot(range(2, 10), distorsiones, marker='o')
    plt.title('Método del Codo')
    plt.xlabel('k')
    plt.ylabel('Inercia')
    pdf.savefig()
    plt.close()

    # Gráfico 5: DBSCAN
    plt.figure()
    plt.scatter(clientes['comisión'], clientes['recencia_dias'],
                c=clientes['cluster_dbscan'], cmap='Set1', s=50)
    plt.xlabel('Comisión Total')
    plt.ylabel('Recencia (días)')
    plt.title('Clusters con DBSCAN')
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # Gráfico 6: Histograma de retención
    plt.figure()
    sns.histplot(data=clientes, x='recencia_dias', hue='retencion', bins=30, kde=True)
    plt.title("Distribución de Recencia según Retención")
    pdf.savefig()
    plt.close()

    # Gráfico 7: Boxplot
    plt.figure()
    sns.boxplot(data=clientes, x='retencion', y='recencia_dias')
    plt.title("Boxplot de Recencia por Clase de Retención")
    pdf.savefig()
    plt.close()

    # Gráfico 8: Evaluación de umbrales
    plt.figure()
    plt.plot(resultados_df['umbral'], resultados_df['auc'], label='AUC')
    plt.plot(resultados_df['umbral'], resultados_df['f1'], label='F1')
    plt.xlabel("Umbral de Recencia (días)")
    plt.ylabel("Métrica")
    plt.title("Evaluación de distintos umbrales de recencia")
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()