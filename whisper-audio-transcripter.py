from flask import Flask, request, render_template, jsonify, send_file, abort
import whisper
import os
from werkzeug.utils import secure_filename
import time
import requests
from dotenv import load_dotenv
from models import MODELS, PROMPT_TEMPLATE
import openai

# Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Flask App Configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['TEXT_FOLDER'] = 'texts/'
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'm4a'}

# Whisper Model Loading
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded.")

# Ensure upload and text folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEXT_FOLDER'], exist_ok=True)

# Hugging Face API Configuration
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/get_models', methods=['GET'])
def get_models():
    return jsonify({"models": MODELS})

@app.route('/get_uploaded_files', methods=['GET'])
def get_uploaded_files():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(filename):
            file_info = {'audio': filename}
            base_name = os.path.splitext(filename)[0]
            transcript_name = f"{base_name}.txt"
            summary_name = f"{base_name}.md"

            # Prüfen, ob das Transkript existiert
            transcript_path = os.path.join(app.config['TEXT_FOLDER'], transcript_name)
            if os.path.exists(transcript_path):
                file_info['transcript'] = transcript_name

            # Prüfen, ob das Protokoll existiert
            summary_path = os.path.join(app.config['TEXT_FOLDER'], summary_name)
            if os.path.exists(summary_path):
                file_info['summary'] = summary_name

            files.append(file_info)
    return jsonify({'files': files})

@app.route('/get_prompt_template', methods=['GET'])
def get_prompt_template():
    return jsonify({"prompt_template": PROMPT_TEMPLATE})

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

    if not allowed_file(file.filename):
        return jsonify({"error": "Ungültiger Dateityp"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    print(f"File saved at: {filepath}")

    # Process the file with Whisper
    try:
        start_time = time.time()
        print("Starting transcription...")
        result = model.transcribe(filepath)
        end_time = time.time()
        print("Transcription completed.")
    except Exception as e:
        print(f"Transcription error: {e}")
        return jsonify({"error": "Fehler bei der Transkription"}), 500

    transcript = result['text']
    processing_time = round(end_time - start_time, 2)

    # Save the transcript
    text_filename = f"{os.path.splitext(filename)[0]}.txt"
    text_filepath = os.path.join(app.config['TEXT_FOLDER'], text_filename)
    with open(text_filepath, 'w') as text_file:
        text_file.write(transcript)
    print(f"Transcript saved at: {text_filepath}")

    return jsonify({"transcript": transcript, "processing_time": processing_time})

@app.route('/upload_existing', methods=['POST'])
def upload_existing():
    data = request.json
    audio_file = data.get('audio')

    if not audio_file:
        return jsonify({"error": "Keine Audiodatei angegeben"}), 400

    filename = secure_filename(audio_file)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Audiodatei nicht gefunden"}), 404

    # Process the file with Whisper
    try:
        start_time = time.time()
        print("Starting transcription of existing file...")
        result = model.transcribe(filepath)
        end_time = time.time()
        print("Transcription completed.")
    except Exception as e:
        print(f"Transcription error: {e}")
        return jsonify({"error": "Fehler bei der Transkription"}), 500

    transcript = result['text']
    processing_time = round(end_time - start_time, 2)

    # Save the transcript
    text_filename = f"{os.path.splitext(filename)[0]}.txt"
    text_filepath = os.path.join(app.config['TEXT_FOLDER'], text_filename)
    with open(text_filepath, 'w') as text_file:
        text_file.write(transcript)
    print(f"Transcript saved at: {text_filepath}")

    return jsonify({"transcript": transcript, "processing_time": processing_time})

@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    data = request.json
    model_key = data.get('model')
    transcript = data.get('transcript')
    audio_filename = data.get('audio_filename')

    if not model_key or model_key not in MODELS:
        return jsonify({"error": "Ungültiges Modell ausgewählt"}), 400

    if not transcript:
        return jsonify({"error": "Kein Transkript vorhanden"}), 400

    if not audio_filename:
        return jsonify({"error": "Kein Audiodateiname angegeben"}), 400

    model_info = MODELS[model_key]
    api_type = model_info['api']
    model_id = model_info['model_id']

    # Verwenden des zentral verwalteten Prompts
    prompt = PROMPT_TEMPLATE.format(transcript=transcript)
    print(f"Using prompt: \n{prompt}")

    # Kürzen Sie den Prompt für Modelle mit Eingabelängenbegrenzung
    max_input_length = 1024  # Passen Sie dies je nach Modell an
    if len(prompt) > max_input_length:
        prompt = prompt[:max_input_length]
        print(f"Prompt truncated to {max_input_length} characters.")

    try:
        if api_type == 'openai':
            print(f"Sending request to OpenAI API with model {model_id}...")
            response = openai.ChatCompletion.create(
                model=model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7,
            )
            print(f"OpenAI response: {response}")

            # Extrahieren der generierten Zusammenfassung
            summary = response['choices'][0]['message']['content']
            print("OpenAI API request successful.")

        elif api_type == 'huggingface':
            print(f"Sending request to Hugging Face API with model {model_id}...")

            headers = {
                "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            }

            # Für Summarization-Modelle wie facebook/bart-large-cnn benötigen Sie keinen komplexen Payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 150,  # Setzen Sie dies auf einen angemessenen Wert für die Ausgabe
                    "min_length": 30,   # Optional: Mindestlänge der Zusammenfassung
                    "do_sample": False  # Für deterministische Ergebnisse
                }
            }

            response = requests.post(
                f"{HUGGINGFACE_API_URL}{model_id}",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            response_data = response.json()
            print(f"Hugging Face response: {response_data}")

            # Extrahieren der Zusammenfassung aus 'summary_text'
            if isinstance(response_data, dict) and 'summary_text' in response_data:
                summary = response_data['summary_text']
            elif isinstance(response_data, list) and 'summary_text' in response_data[0]:
                summary = response_data[0]['summary_text']
            else:
                return jsonify({"error": "Keine Zusammenfassung erhalten"}), 500

            print("Hugging Face API request successful.")

        else:
            return jsonify({"error": "Ungültiger API-Typ"}), 500

    except Exception as e:
        print(f"API error: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"API Response: {response.text}")
        return jsonify({"error": str(e)}), 500

    # Speichern des Protokolls mit dem gleichen Basename wie die Audiodatei
    base_name = os.path.splitext(audio_filename)[0]
    summary_filename = f"{base_name}.md"
    summary_filepath = os.path.join(app.config['TEXT_FOLDER'], summary_filename)
    with open(summary_filepath, 'w') as summary_file:
        summary_file.write(summary)
    print(f"Meeting-Protokoll gespeichert unter: {summary_filepath}")

    return jsonify({"meeting_summary": summary, "summary_file": summary_filename})



@app.route('/get_text/<filename>', methods=['GET'])
def get_text(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['TEXT_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "Datei nicht gefunden"}), 404

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    audio_filename = data.get('audio_filename')

    if not audio_filename:
        return jsonify({"error": "Kein Audiodateiname angegeben"}), 400

    audio_filepath = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
    if not os.path.exists(audio_filepath):
        return jsonify({"error": "Audiodatei nicht gefunden"}), 400

    # Transkription durchführen
    print(f"Transkribiere Audiodatei: {audio_filename}")
    result = model.transcribe(audio_filepath, language='de')

    # Speichern des Transkripts mit dem gleichen Basename wie die Audiodatei
    base_name = os.path.splitext(audio_filename)[0]
    transcript_filename = f"{base_name}.txt"
    transcript_filepath = os.path.join(app.config['TEXT_FOLDER'], transcript_filename)
    with open(transcript_filepath, 'w') as transcript_file:
        transcript_file.write(result['text'])
    print(f"Transkript gespeichert unter: {transcript_filepath}")

    return jsonify({"message": "Transkription erfolgreich", "transcript": transcript_filename})

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(debug=debug_mode)
