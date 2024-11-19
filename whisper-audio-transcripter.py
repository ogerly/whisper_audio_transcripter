from flask import Flask, request, render_template, jsonify
import whisper
import os
from werkzeug.utils import secure_filename
import time
import requests

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
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/YOUR_MODEL_NAME_HERE"
HUGGINGFACE_API_KEY = "YOUR_HUGGINGFACE_API_KEY_HERE"

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

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

    # Hugging Face API Aufruf zur Erstellung des Meeting Protokolls
    prompt = f"Erstelle ein Meeting-Protokoll basierend auf folgendem Transkript: {transcript}"
    try:
        print("Sende Anfrage an Hugging Face API...")
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json={"inputs": prompt})
        response.raise_for_status()
        summary = response.json()[0]['generated_text']
        print("Hugging Face API Anfrage erfolgreich.")
    except Exception as e:
        print(f"Fehler bei der Hugging Face API Anfrage: {e}")
        return jsonify({"error": "Fehler bei der Protokollerstellung"}), 500

    # Gebe das Transkript und das Meeting Protokoll zurück
    return jsonify({"transcript": transcript, "processing_time": processing_time, "meeting_summary": summary})

if __name__ == '__main__':
    app.run(debug=True)

# Hinweis: Die index.html Datei muss separat im templates-Ordner gespeichert werden.
