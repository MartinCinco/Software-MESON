"""
Este módulo inicia una aplicación Flask simple para manejar rutas y renderizar plantillas.
"""
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    """Ruta principal que renderiza index.html"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
