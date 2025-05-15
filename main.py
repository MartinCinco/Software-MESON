import threading
import time
import webview
from app import create_app

app = create_app()

def start_flask():
    app.run(port=5000)

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    time.sleep(2)
    print("Lanzando ventana...")
    webview.create_window("Software-MESON", "http://127.0.0.1:5000")
    webview.start(debug=True)
