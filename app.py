from flask import Flask, request, send_file, send_from_directory, jsonify, url_for
from werkzeug.utils import secure_filename
import os
from docx import Document
from gtts import gTTS
import logging

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO)

LANGUAGES = {
    'en': 'English (Indian)',
    'hi': 'Hindi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'gu': 'Gujarati',
    'mr': 'Marathi',
    'bn': 'Bengali',
    'pa': 'Punjabi',
}

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error('No file part in the request')
        return jsonify(error='No file part'), 400
    file = request.files['file']
    if file.filename == '':
        app.logger.error('No selected file')
        return jsonify(error='No selected file'), 400
    language = request.form.get('language', 'en')
    if language not in LANGUAGES:
        app.logger.error('Invalid language code')
        return jsonify(error='Invalid language code'), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        app.logger.info(f'Saving file to {file_path}')
        file.save(file_path)
        return convert_to_speech(file_path, filename, language)
    app.logger.error('File upload failed')
    return jsonify(error='File upload failed'), 500

def convert_to_speech(file_path, filename, language):
    try:
        app.logger.info(f'Converting file {file_path} to speech')
        doc = Document(file_path)
        full_text = '\n'.join([para.text for para in doc.paragraphs])
        app.logger.info(f'Extracted text: {full_text[:100]}...')  # Log the first 100 characters of text
        tts = gTTS(text=full_text, lang=language)
        output_filename = os.path.splitext(filename)[0] + '.mp3'
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        tts.save(output_path)
        app.logger.info(f'File converted successfully, saved to {output_path}')
        return jsonify({
            'message': 'File converted successfully',
            'url': url_for('download_file', filename=output_filename)
        })
    except Exception as e:
        app.logger.error(f'Error during conversion: {e}')
        return jsonify(error=str(e)), 500

@app.route('/output/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
