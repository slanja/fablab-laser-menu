import os
import subprocess
import win32print
import win32api
import webbrowser
from threading import Timer
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
client_path = os.path.normpath(os.path.join(root_dir, 'client'))

app = Flask(__name__, static_folder=client_path, static_url_path='')
CORS(app)

# ==========================================
SIMULATION_MODE = False 
PORT = 5000
# ==========================================

BASE_PATH = os.path.join(client_path, 'assets', 'svg')

def get_trotec_printer_name():
    if SIMULATION_MODE:
        return "Virtuální Laser (Simulace)"
    try:
        printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        trotec = [p for p in printers if "Trotec" in p]
        return trotec[0] if trotec else None
    except:
        return None

PRINTER_NAME = get_trotec_printer_name()

def open_browser():
    url = f"http://localhost:{PORT}"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    try:
        if os.path.exists(chrome_path):
            subprocess.Popen([chrome_path, f"--app={url}"])
        else:
            webbrowser.open(url)
    except:
        webbrowser.open(url)

def find_motif_path(motif_id):
    if not os.path.exists(BASE_PATH): return None
    for category in os.listdir(BASE_PATH):
        cat_path = os.path.join(BASE_PATH, category)
        if os.path.isdir(cat_path):
            file = os.path.join(cat_path, f"{motif_id}.svg")
            if os.path.exists(file): return os.path.abspath(file)
    return None

def send_to_laser(file_path):
    if SIMULATION_MODE:
        print(f"🛠️ [SIMULACE] Tisk: {file_path}")
        return True
    try:
        subprocess.run(["inkscape", "--export-type=pdf", f"--print={PRINTER_NAME}", file_path], check=True, timeout=10)
        return True
    except:
        try:
            win32api.ShellExecute(0, "printto", file_path, f'"{PRINTER_NAME}"', ".", 0)
            return True
        except Exception as e:
            print(f"❌ Chyba tisku: {e}")
            return False

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/motifs')
def get_motifs():
    """Vrací seznam motivů. POZOR: Vyžaduje, aby SVGs byly v podsložkách (kategoriích)."""
    motifs = []
    
    if not os.path.exists(BASE_PATH):
        print(f"⚠️ CHYBA: Složka s motivy neexistuje: {BASE_PATH}")
        return jsonify([])

    # Procházení kategorií (složek v assets/svg)
    categories = [d for d in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, d))]
    
    for category in categories:
        cat_path = os.path.join(BASE_PATH, category)
        for filename in os.listdir(cat_path):
            if filename.endswith('.svg'):
                motifs.append({
                    "id": filename.replace('.svg', ''),
                    "category": category,
                    "src": f"assets/svg/{category}/{filename}"
                })
    
    print(f"✅ API doručilo {len(motifs)} motivů z {len(categories)} kategorií.")
    return jsonify(motifs)

@app.route('/api/print', methods=['POST'])
def print_job():
    data = request.json
    success_count = 0
    for motif_id, quantity in data.items():
        file_path = find_motif_path(motif_id)
        if file_path:
            for _ in range(int(quantity)):
                if send_to_laser(file_path): success_count += 1
    return jsonify({"status": "success", "sent_jobs": success_count}), 200

if __name__ == '__main__':
    print(f"🚀 Spouštění Laser Menu na portu {PORT}...")
    print(f"📁 Databáze motivů: {BASE_PATH}")
    print(f"🖨️ Tisková tiskárna: {PRINTER_NAME}")
    
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(2.0, open_browser).start()

    app.run(host='0.0.0.0', port=PORT, debug=True)