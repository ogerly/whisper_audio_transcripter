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
hf_headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/get_models', methods=['GET'])
def get_models():
    return jsonify({"models": MODELS})

@app.route('/get_uploaded_files', methods=['GET'])
def get_uploaded_files():
    files = []
    for audio_file in os.listdir(app.config['UPLOAD_FOLDER']):
        audio_name, audio_ext = os.path.splitext(audio_file)
        text_file = f"{audio_name}.txt"
        text_path = os.path.join(app.config['TEXT_FOLDER'], text_file)
        transcript_available = os.path.exists(text_path)
        summary_file = f"summary_{text_file}"
        summary_path = os.path.join(app.config['TEXT_FOLDER'], summary_file)
        summary_available = os.path.exists(summary_path)
        files.append({
            "audio": audio_file,
            "transcript": text_file if transcript_available else None,
            "summary": summary_file if summary_available else None
        })
    return jsonify({"files": files})

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

    if not model_key or model_key not in MODELS:
        return jsonify({"error": "Ungültiges Modell ausgewählt"}), 400

    if not transcript:
        return jsonify({"error": "Kein Transkript vorhanden"}), 400

    model_info = MODELS[model_key]
    api_type = model_info['api']
    model_id = model_info['model_id']

    # Verwenden des zentral verwalteten Prompts
    prompt = PROMPT_TEMPLATE.format(transcript=transcript)
    print(f"Using prompt: {prompt}")

    try:
        if api_type == 'huggingface':
            print(f"Sending request to Hugging Face API with model {model_id}...")
            response = requests.post(
                f"{HUGGINGFACE_API_URL}{model_id}",
                headers=hf_headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_length": 2024,
                        "num_beams": 4,
                        "early_stopping": True
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            response_data = response.json()
            print(f"Hugging Face response: {response_data}")

            if isinstance(response_data, dict) and 'error' in response_data:
                return jsonify({"error": response_data['error']}), 500

               # Extrahieren der generierten Zusammenfassung
            summary = response_data.get('generated_text', None)
            if not summary:
                return jsonify({"error": "Keine Zusammenfassung erhalten"}), 500

            print("Hugging Face API request successful.")

        elif api_type == 'openai':
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

        else:
            return jsonify({"error": "Ungültiger API-Typ"}), 500

    except Exception as e:
        print(f"API error: {e}")
        return jsonify({"error": str(e)}), 500

    # Speichern des Protokolls
    summary_filename = f"summary_{int(time.time())}.md"  # Speichern als Markdown-Datei
    summary_filepath = os.path.join(app.config['TEXT_FOLDER'], summary_filename)
    with open(summary_filepath, 'w') as summary_file:
        summary_file.write(summary)
    print(f"Meeting summary saved at: {summary_filepath}")

    return jsonify({"meeting_summary": summary, "summary_file": summary_filename})





@app.route('/get_text/<filename>', methods=['GET'])
def get_text(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['TEXT_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "Datei nicht gefunden"}), 404

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(debug=debug_mode)
