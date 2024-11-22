**Aktualisiertes README.md**

---

# Whisper Audio Transcripter

## Beschreibung

Ein Python-basiertes Tool zur Transkription von Audiodateien und automatischen Erstellung von Meetingprotokollen. Es verwendet das OpenAI Whisper-Modell zur Transkription und sowohl die OpenAI ChatGPT API als auch die Hugging Face Inference API zur Erstellung von Zusammenfassungen. Das Projekt basiert auf Flask als Backend und bietet eine Weboberfläche zum Hochladen von Audiodateien, Anzeigen der Transkripte und Generieren von Meetingprotokollen.


![Bildschirmfoto vom 2024-11-22 18-48-17](https://github.com/user-attachments/assets/537657fc-91b7-4a3f-bb58-c5760b7bf88c)


## Features

- **Audiodateien hochladen**: Unterstützt MP3, WAV und M4A Formate.
- **Transkription mit Whisper**: Nutzt das OpenAI Whisper-Modell zur präzisen Spracherkennung.
- **Automatische Meetingprotokolle**: Generiert strukturierte Protokolle mit der OpenAI ChatGPT API oder der Hugging Face Inference API.
- **Modellauswahl**: Wählen Sie zwischen verschiedenen Modellen für die Zusammenfassung.
- **Unterstützung der deutschen Sprache**: Optimiert für die Verarbeitung deutscher Texte.
- **Download-Funktion**: Laden Sie Transkripte und Protokolle als Markdown-Dateien herunter.
- **Benutzerfreundliches Frontend**: Intuitive Weboberfläche mit Fortschrittsanzeigen.

## Technologie-Stack

- **Backend**: Flask
- **Spracherkennung**: OpenAI Whisper
- **Zusammenfassung**: OpenAI ChatGPT API & Hugging Face Inference API
- **Frontend**: HTML, Bootstrap, jQuery

## Anforderungen

- **Python**: Version 3.7 oder höher
- **Abhängigkeiten**: Siehe `requirements.txt`
- **FFmpeg**: Für die Audioverarbeitung mit Whisper erforderlich
- **API-Schlüssel**:
  - **OpenAI API-Schlüssel**: Für die Nutzung der OpenAI ChatGPT API
  - **Hugging Face API-Schlüssel**: Für die Nutzung der Hugging Face Inference API

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/whisper-audio-transcripter.git
cd whisper-audio-transcripter
```

### 2. Virtuelle Umgebung erstellen (optional, aber empfohlen)

```bash
python3 -m venv venv
source venv/bin/activate  # Für Windows: venv\Scripts\activate
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 4. FFmpeg installieren

- **Linux (Debian/Ubuntu)**:

  ```bash
  sudo apt-get install ffmpeg
  ```

- **macOS (mit Homebrew)**:

  ```bash
  brew install ffmpeg
  ```

- **Windows**:

  - Laden Sie FFmpeg von der [offiziellen Website](https://ffmpeg.org/download.html) herunter.
  - Folgen Sie einer Anleitung, um FFmpeg zu installieren und dem PATH hinzuzufügen.

### 5. API-Schlüssel einrichten

#### a. OpenAI API-Schlüssel

- **Registrierung**: Erstellen Sie ein Konto bei [OpenAI](https://platform.openai.com/).
- **API-Schlüssel erstellen**: Gehen Sie zu [API-Schlüssel](https://platform.openai.com/account/api-keys) und erstellen Sie einen neuen Schlüssel.
- **Kostenhinweis**: Die Nutzung der OpenAI API kann kostenpflichtig sein. Überprüfen Sie Ihre [Abrechnungsinformationen](https://platform.openai.com/account/billing/overview) und stellen Sie sicher, dass Sie über ausreichendes Guthaben verfügen.

#### b. Hugging Face API-Schlüssel

- **Registrierung**: Erstellen Sie ein Konto bei [Hugging Face](https://huggingface.co/join).
- **Access Token erstellen**: Gehen Sie zu [Einstellungen > Access Tokens](https://huggingface.co/settings/tokens) und erstellen Sie ein neues Token mit Lesezugriff.
- **Kostenhinweis**: Einige Modelle oder Dienste auf Hugging Face können kostenpflichtig sein oder erfordern spezielle Berechtigungen.

#### c. Umgebungsvariablen einrichten

Erstellen Sie eine `.env`-Datei im Hauptverzeichnis und fügen Sie Ihre API-Schlüssel hinzu:

```bash
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

**Hinweis**: Stellen Sie sicher, dass die `.env`-Datei nicht in Ihr Versionskontrollsystem aufgenommen wird, um Ihre Schlüssel zu schützen.

### 6. Anwendung starten

```bash
python3 whisper-audio-transcripter.py
```

Die Anwendung läuft nun auf `http://127.0.0.1:5000`.

## Verwendung

### 1. Weboberfläche öffnen

- Öffnen Sie einen Webbrowser und navigieren Sie zu `http://127.0.0.1:5000`.

### 2. Audiodatei hochladen

- Klicken Sie auf "Datei auswählen" und wählen Sie eine Audiodatei (MP3, WAV, M4A) aus.
- Klicken Sie auf "Datei hochladen", um die Audiodatei zum Server zu übertragen.

### 3. Audiodatei transkribieren

- In der Liste der hochgeladenen Dateien sehen Sie Ihre Audiodatei.
- Klicken Sie auf "Transkribieren", um die Audiodatei in Text umzuwandeln.
- Der Fortschritt wird im Frontend angezeigt.

### 4. Transkript anzeigen oder herunterladen

- Nach Abschluss der Transkription können Sie das Transkript anzeigen oder als Textdatei herunterladen.

### 5. Modell für die Zusammenfassung auswählen

- Wählen Sie ein Modell aus der Liste der verfügbaren Modelle. Diese sind nach API (OpenAI oder Hugging Face) gekennzeichnet.
- Achten Sie darauf, ein Modell zu wählen, das die deutsche Sprache unterstützt.

### 6. Meetingprotokoll erstellen

- Klicken Sie auf "Protokoll erstellen", um basierend auf dem Transkript ein Meetingprotokoll zu generieren.
- Das Meetingprotokoll wird im Frontend angezeigt und kann ebenfalls heruntergeladen werden.

## Anpassung des Prompt-Templates

Das Prompt-Template, das zur Generierung der Meetingprotokolle verwendet wird, befindet sich in der Datei `models.py` unter `PROMPT_TEMPLATE`. Sie können dieses Template nach Ihren Bedürfnissen anpassen, um die Ausgabe des Modells zu beeinflussen.

**Beispiel:**

```python
PROMPT_TEMPLATE = """
Generiere ein professionelles und strukturiertes Meetingprotokoll basierend auf dem folgenden Transkript:

{transcript}

Das Protokoll sollte folgende Abschnitte enthalten:
- Datum
- Teilnehmer
- Zusammenfassung
- Agenda-Punkte
- Entscheidungen
- Aktionspunkte
- Nächste Schritte
"""
```

## Hinweise zur Nutzung der APIs

- **API-Schlüssel Sicherheit**

  - Bewahren Sie Ihre API-Schlüssel sicher auf.
  - Geben Sie Ihre Schlüssel nicht an Dritte weiter.
  - Stellen Sie sicher, dass die `.env`-Datei nicht öffentlich zugänglich ist.

- **Kosten und Abrechnung**

  - Die Nutzung der OpenAI API und einiger Modelle der Hugging Face API kann kostenpflichtig sein.
  - Überwachen Sie Ihre API-Nutzung, um ungewollte Kosten zu vermeiden.
  - Überprüfen Sie regelmäßig Ihre Abrechnungsinformationen bei OpenAI und Hugging Face.

- **Nutzungsbedingungen**

  - Achten Sie darauf, die jeweiligen Nutzungsbedingungen von OpenAI und Hugging Face einzuhalten.
  - Verarbeiten Sie keine vertraulichen oder urheberrechtlich geschützten Inhalte ohne entsprechende Berechtigung.

## Anforderungen an die Modelle

- **Unterstützung der deutschen Sprache**

  - Da die Anwendung mit deutschen Texten arbeitet, sollten Sie Modelle wählen, die Deutsch unterstützen.
  - **Empfohlene Modelle**:
    - **OpenAI**: `gpt-3.5-turbo` (unterstützt mehrere Sprachen, einschließlich Deutsch)
    - **Hugging Face**: `ml6team/mt5-small-german-finetune-mlsum` (speziell für deutsche Zusammenfassungen trainiert)

## Beispielkonfiguration der Modelle (`models.py`)

```python
MODELS = {
    "gpt-3.5-turbo": {
        "api": "openai",
        "model_id": "gpt-3.5-turbo"
    },
    "mt5-small-german": {
        "api": "huggingface",
        "model_id": "ml6team/mt5-small-german-finetune-mlsum"
    },
    # Weitere Modelle können hier hinzugefügt werden
}
```

## Fehlerbehebung

### 1. Fehler bei der Protokollerstellung

- **Mögliche Ursachen**:
  - API-Schlüssel sind nicht korrekt oder fehlen.
  - API-Kontingent wurde überschritten.
  - Netzwerkprobleme.

- **Lösungen**:
  - Überprüfen Sie Ihre `.env`-Datei und stellen Sie sicher, dass die API-Schlüssel korrekt sind.
  - Loggen Sie sich bei OpenAI und Hugging Face ein, um Ihr Kontingent und Ihre Abrechnungsinformationen zu überprüfen.
  - Prüfen Sie Ihre Internetverbindung.

### 2. Unvollständige oder fehlerhafte Ausgaben

- **Mögliche Ursachen**:
  - Das gewählte Modell unterstützt die deutsche Sprache nicht ausreichend.
  - Der Prompt ist zu komplex oder unklar.

- **Lösungen**:
  - Wählen Sie ein anderes Modell, das besser für die deutsche Sprache geeignet ist.
  - Passen Sie das `PROMPT_TEMPLATE` an und vereinfachen Sie es gegebenenfalls.

### 3. Allgemeine Tipps

- **Konsolenausgaben überprüfen**: Sowohl im Backend (Terminal) als auch im Frontend (Browser-Konsole) können hilfreiche Fehlermeldungen erscheinen.
- **Server neu starten**: Nach Änderungen am Code oder den Umgebungsvariablen den Server neu starten.
- **Browser-Cache leeren**: Bei Änderungen im Frontend kann es hilfreich sein, den Cache zu leeren oder im Inkognito-Modus zu testen.

## Lizenz

Dieses Projekt steht unter der [MIT Lizenz](LICENSE).

## Beitragende

Beiträge sind willkommen! Bitte öffnen Sie ein Issue oder einen Pull Request, um zur Verbesserung dieses Projekts beizutragen.

---

**Hinweis**: Stellen Sie sicher, dass Sie die aktuellsten Versionen der verwendeten Bibliotheken und Modelle verwenden. Lesen Sie die Dokumentation der APIs sorgfältig, um optimale Ergebnisse zu erzielen.

**Wichtig**: Denken Sie daran, dass die Nutzung von KI-Modellen und APIs ethische Überlegungen mit sich bringt. Seien Sie verantwortlich bei der Verarbeitung von Daten und achten Sie auf Datenschutz und Urheberrechte.
