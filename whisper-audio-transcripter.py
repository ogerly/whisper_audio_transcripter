from flask import Flask, request, render_template, jsonify
import whisper
import os
from werkzeug.utils import secure_filename
import time
import requests
from dotenv import load_dotenv
from models_config import MODELS  # Importiere das Modell aus einer separaten Datei

# Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Flask App Configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Whisper Model Loading
print("Lade Whisper-Modell...")
model = whisper.load_model("base")  # Ändere den Modeltyp bei Bedarf, z.B. "small", "medium", "large"
print("Whisper-Modell geladen.")

# Sicherstellen, dass der Upload-Ordner existiert
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Hugging Face API Configuration
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

@app.route('/get_models', methods=['GET'])
def get_models():
    return jsonify({"models": MODELS})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'audio' not in request.files:
        return jsonify({"error": "Keine Datei hochgeladen"}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "Keine Datei ausgewählt"}), 400

    # Speichere die Datei sicher
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    print(f"Datei erfolgreich gespeichert unter: {filepath}")

    # Verarbeite die Datei mit Whisper
    try:
        start_time = time.time()
        print("Starte Transkription...")
        result = model.transcribe(filepath)
        end_time = time.time()
        print("Transkription abgeschlossen.")
    except Exception as e:
        print(f"Fehler während der Transkription: {e}")
        return jsonify({"error": "Fehler bei der Transkription"}), 500

    transcript = result['text']
    processing_time = round(end_time - start_time, 2)

    return jsonify({"transcript": transcript, "processing_time": processing_time})

@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    data = request.json
    model_key = data.get('model')
    transcript = data.get('transcript')

    if not model_key or model_key not in MODELS:
        return jsonify({"error": "Ungültiges Modell ausgewählt"}), 400
    
    if not transcript:
        return jsonify({"error": "Kein Transkript vorhanden"}), 400

    prompt = (
        f"Erstelle ein Meeting-Protokoll basierend auf folgendem Transkript: {transcript}\n"
        f"Fasse die wichtigsten Punkte des Meetings zusammen, liste wichtige Entscheidungen und Termine auf."
    )
    print(f"Verwendeter Prompt: {prompt}")

    try:
        print(f"Sende Anfrage an Hugging Face API mit Modell {model_key}...")
        response = requests.post(f"{HUGGINGFACE_API_URL}{MODELS[model_key]}", headers=headers, json={"inputs": prompt})
        response.raise_for_status()
        response_data = response.json()
        print(f"Antwort von Hugging Face: {response_data}")
        
        summary = response_data['generated_text'] if 'generated_text' in response_data else response_data[0]['generated_text']
        print("Hugging Face API Anfrage erfolgreich.")
    except Exception as e:
        print(f"Fehler bei der Hugging Face API Anfrage: {e}")
        return jsonify({"error": "Fehler bei der Protokollerstellung"}), 500

    return jsonify({"meeting_summary": summary})

if __name__ == '__main__':
    try:
        import dotenv
    except ImportError:
        print("Fehler: Das Modul 'python-dotenv' fehlt. Installiere es mit 'pip install python-dotenv'.")
        exit(1)
    app.run(debug=True)

# Hinweis: Die index.html Datei muss separat im templates-Ordner gespeichert werden.
