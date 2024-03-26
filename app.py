from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
import io
import os
from pydub import AudioSegment
# import Ambient_Pipeline as ap
import numpy as np
import tempfile
import torch
import torchaudio
import subprocess


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_mp3_to_wav(input_filepath, output_filepath):
    command = ['ffmpeg', '-i', input_filepath, '-ar', '44100', output_filepath]
    subprocess.run(command, check=True)
    
def load_wav_as_np_array(filepath_wav):
    waveform, sample_rate = torchaudio.load(filepath_wav)
    # Convert the tensor to a numpy array
    np_waveform = waveform.numpy()
    return np_waveform, sample_rate

@app.route('/upload', methods=['POST'])
def upload():
    if 'audioFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['audioFile']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'No selected file or invalid file type'}), 400
    
    filename = "user_recording.mp3"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    filename_wav = "user_recording.wav"
    filepath_wav = os.path.join(UPLOAD_FOLDER, filename_wav)
    
    # Convert MP3 to WAV using ffmpeg directly
    try:
        convert_mp3_to_wav(filepath, filepath_wav)
        # Now you can work with the WAV file
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Failed to process audio file with ffmpeg'}), 500
    
    # Load the WAV file as a NumPy array
    try:
        sound, sr = load_wav_as_np_array(filepath_wav)
        print(f"Loaded WAV with sample rate: {sr}")
    except Exception as e:
        return jsonify({'error': f'Failed to load WAV file: {e}'}), 500

    # - Feed that into the Ambient Pipeline
   
    #TODO

    # - Save that audio as an mp3 to the uploads folder (DONE)
    
    processed_file_name = 'user_recording_backing.mp3'
    processed_filepath = os.path.join(UPLOAD_FOLDER, processed_file_name)  # Build the full path for the processed file
    # processed_audio_file.save(processed_filepath)
    
    # - Serve that file location to the user (DONE) 

    if os.path.exists(filepath) and os.path.exists(processed_filepath):
        return jsonify({
            'original': filename,
            'processed': 'user_recording_backing.mp3'
        })
    else:
        return jsonify({'error': 'Error processing file'}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)    
    
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
