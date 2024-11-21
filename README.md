# Whisper Audio Transcripter

## Beschreibung

Ein einfaches Python-Tool, das Audiodateien eines Meetings transkribiert und automatisch Meeting-Protokolle erstellt. Es verwendet das OpenAI Whisper-Modell zur Transkription und das Hugging Face API-Modell zur Erstellung von Zusammenfassungen. Das Projekt basiert auf Flask als Backend, bietet eine Upload-Möglichkeit für Audiodateien und gibt nach Verarbeitung das vollständige Transkript sowie eine Zusammenfassung aus.


![image](https://github.com/user-attachments/assets/d150f934-d04a-40b2-8098-2f47c30d367c)

## Features
- Hochladen von MP3-Audiodateien zur Verarbeitung
- Transkription von Meetings mit Whisper
- Erstellung eines Meeting-Protokolls über die Hugging Face API
- Fortschrittsanzeige für die Verarbeitung im Frontend

## Technologie-Stack
- **Backend**: Flask
- **Spracherkennung**: OpenAI Whisper
- **Zusammenfassung**: Hugging Face API
- **Frontend**: HTML, Bootstrap, jQuery

## Anforderungen
- Python 3.7+
- Flask
- OpenAI Whisper
- Requests Library
- Werkzeug
- FFmpeg (für Whisper erforderlich)

## Installation
1. Klone das Repository:
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/whisper-audio-transcripter.git
   cd whisper-audio-transcripter
   ```

2. Installiere die benötigten Python-Pakete:
   ```bash
   pip install -r requirements.txt
   ```

3. Installiere FFmpeg (Linux):
   ```bash
   sudo apt-get install ffmpeg
   ```

4. Erstelle einen Ordner `templates` und speichere darin die `index.html`-Datei.

5. Setze deinen Hugging Face API Key ein:
   - Öffne die Python-Datei `whisper-audio-transcripter.py`
   - Ersetze `YOUR_HUGGINGFACE_API_KEY_HERE` durch deinen API-Schlüssel von Hugging Face

6. Starte die Anwendung:
   ```bash
   python3 whisper-audio-transcripter.py
   ```

## index.html Beispiel
Hier ist ein Beispiel für die `index.html`, die im `templates`-Ordner gespeichert werden sollte:

```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meeting Transkription</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
</head>
<body>
<div class="container mt-5">
    <h2>Meeting-Transkription hochladen</h2>
    <form id="uploadForm">
        <div class="mb-3">
            <input type="file" name="audio" id="audio" class="form-control" accept="audio/mpeg">
        </div>
        <button type="submit" class="btn btn-primary">Hochladen und Transkribieren</button>
    </form>
    <div id="progress" class="progress mt-3" style="display: none;">
        <div class="progress-bar" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
    </div>
    <div id="result" class="mt-3"></div>
</div>

<script>
    $("#uploadForm").on("submit", function(event) {
        event.preventDefault();
        let formData = new FormData();
        let fileInput = $('#audio')[0].files[0];
        formData.append('audio', fileInput);

        $("#progress").show();
        $(".progress-bar").css("width", "0%");
        $(".progress-bar").attr("aria-valuenow", 0);

        $.ajax({
            url: "/upload",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function(evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = (evt.loaded / evt.total) * 100;
                        $(".progress-bar").css("width", percentComplete + "%");
                        $(".progress-bar").attr("aria-valuenow", percentComplete);
                    }
                }, false);
                return xhr;
            },
            success: function(response) {
                $("#progress").hide();
                $("#result").html(`<p>Transkript: ${response.transcript}</p><p>Meeting Protokoll: ${response.meeting_summary}</p><p>Bearbeitungszeit: ${response.processing_time} Sekunden</p>`);
            },
            error: function() {
                $("#progress").hide();
                $("#result").html(`<p class="text-danger">Fehler beim Hochladen oder Transkribieren der Datei</p>`);
            }
        });
    });
</script>
</body>
</html>
```

## Demo
Sobald die Anwendung läuft, öffne einen Browser und navigiere zu `http://127.0.0.1:5000`. Du wirst ein einfaches Formular sehen, in das du eine MP3-Datei hochladen kannst. Nachdem die Datei verarbeitet wurde, wird dir sowohl das Transkript als auch das Meeting-Protokoll angezeigt.

## Verwendungshinweise
- Diese Anwendung sollte nicht in einer Produktionsumgebung verwendet werden, da das Hugging Face Modell, das hier genutzt wird, keine hohen Sicherheitsstandards aufweist.
- Verwende für Produktionszwecke eine geeignete WSGI-Lösung (z.B. gunicorn) und hoste die Anwendung auf einem geeigneten Server.

## Lizenz
MIT License. Weitere Informationen findest du in der `LICENSE`-Datei.

## Beitragende
Pull-Requests und Issues sind willkommen! Fühle dich frei, zur Verbesserung dieses Tools beizutragen.

