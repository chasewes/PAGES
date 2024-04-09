from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
import io
import os
from pydub import AudioSegment
import Ambient_Pipeline as ap
import numpy as np
import tempfile
import torch
import torchaudio
import subprocess
# import librosa
# import scipy.io.wavfile as wavfile


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

UPLOAD_FOLDER = 'uploads'

MAX_DURATION = None #60 # Set to None if you dont want a max


def generate_unique_filepath(directory, filename):
    """
    Generates a unique filepath by appending a number to the filename if the file already exists.

    Args:
        directory (str): The directory where the file will be saved.
        filename (str): The original filename.

    Returns:
        str: A unique filepath where the file can be saved without overwriting existing files.
    """
    # Split the filename into name and extension
    name, extension = os.path.splitext(filename)
    unique_filename = filename  # Start with the original filename
    counter = 1  # Initialize counter for filename numbering

    # Construct the full path to check if the file exists
    filepath = os.path.join(directory, unique_filename)

    # Loop until a unique filepath is found
    while os.path.exists(filepath):
        # Append a counter to the filename to make it unique
        unique_filename = f"{name}_{counter}{extension}"
        filepath = os.path.join(directory, unique_filename)
        counter += 1

    return unique_filename, filepath

def trim_audio_to_length(audio_data, sample_rate, duration_in_seconds=MAX_DURATION):
    """
    Trim a loaded audio clip to a specific length in seconds.

    Args:
        audio_data (numpy.ndarray): The loaded audio data as a NumPy array. Can be mono or stereo.
        sample_rate (int): The sample rate of the audio data.
        duration_in_seconds (int or float): The desired duration of the audio clip in seconds.

    Returns:
        numpy.ndarray: The trimmed audio data.
    """    
    if duration_in_seconds is None or audio_data.shape[-1] <= int(sample_rate * duration_in_seconds):
        return audio_data
    
    # Calculate the number of samples to retain in the trimmed audio
    num_samples_to_retain = int(sample_rate * duration_in_seconds)


    # Check if the audio data is stereo (2 channels) or mono
    if audio_data.ndim == 2:
        # Stereo: Trim both channels
        trimmed_audio = audio_data[:, :num_samples_to_retain]
    else:
        # Mono: Trim the single channel
        trimmed_audio = audio_data[:num_samples_to_retain]

    return trimmed_audio


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_mp3_to_wav(input_filepath, output_filepath):
    command = ['ffmpeg', '-y','-i', input_filepath, '-ar', '44100', output_filepath]
    subprocess.run(command, check=True)
    
def load_wav_as_np_array(filepath_wav):
    waveform, sample_rate = torchaudio.load(filepath_wav)
    # Convert the tensor to a numpy array
    np_waveform = waveform.numpy()
    return np_waveform, sample_rate

# @app.route('/api/recent-uploads')
# def list_recent_uploads():
#     folder_path = './uploads'
#     backing_tracks = [f for f in os.listdir(folder_path) if f.endswith('_backing.mp3')]
#     base_files = [os.path.splitext(f)[0] for f in backing_tracks]  # Remove '_backing.mp3' to get base filename
#     base_files = [file for file in base_files if os.path.exists(os.path.join(folder_path, file + '.mp3')]
#     return jsonify(base_files)

@app.route('/api/recent-uploads')
def list_recent_uploads():
    uploads_dir = './uploads'
    files = os.listdir(uploads_dir)
    demos = []

    for file in files:
        if file.endswith('_backing.mp3'):
            base_name = file.rsplit('_backing.mp3', 1)[0]
            # Search for corresponding main audio file
            main_audio = None
            for ext in ['.mp3', '.wav']:
                if f'{base_name}{ext}' in files:
                    main_audio = f'{base_name}{ext}'
                    break
            if main_audio:
                demos.append({'main': main_audio, 'backing': file})
                
    return jsonify(demos)


@app.route('/upload', methods=['POST'])
def upload():
    if 'audioFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['audioFile']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'No selected file or invalid file type'}), 400
    
    
    # filename = "balrog_audio.mp3"
    
    
    # filepath = os.path.join(UPLOAD_FOLDER, filename)
     # Generate a unique filepath
    updated_filename, filepath = generate_unique_filepath(app.config['UPLOAD_FOLDER'], file.filename)
    
    file.save(filepath)
    
    base_name, ext = os.path.splitext(updated_filename)
    ext = ext.lower()
    # ext = os.path.splitext(filepath)[1].lower()
    print(f"File extension: {ext}")
    
    filepath_wav = ""
    if ext.endswith('wav'):
        filepath_wav = filepath
    elif ext.endswith('mp3'):
        filepath_wav = filepath.replace('.mp3', '.wav')
        
        # Convert MP3 to WAV using ffmpeg directly
        try:
            convert_mp3_to_wav(filepath, filepath_wav)
            # Now you can work with the WAV file
        except subprocess.CalledProcessError as e:
            return jsonify({'error': 'Failed to process audio file with ffmpeg'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400


    # processed_filename = updated_filename.replace('.wav', '_backing.mp3')
    processed_filename = base_name + '_backing.mp3'
    processed_filepath = filepath_wav.replace('.wav', '_backing.mp3')
    
    # file.save(filepath)
    
    # filename_wav = "user_recording.wav"
    # filepath_wav = os.path.join(UPLOAD_FOLDER, filename_wav)
    
    # # Convert MP3 to WAV using ffmpeg directly
    # try:
    #     convert_mp3_to_wav(filepath, filepath_wav)
    #     # Now you can work with the WAV file
    # except subprocess.CalledProcessError as e:
    #     return jsonify({'error': 'Failed to process audio file with ffmpeg'}), 500
    
    # filepath_wav = os.path.join(UPLOAD_FOLDER, 'user_recording_harry_potter.wav')
    
    # Load the WAV file as a NumPy array
    try:
        sound, sr = load_wav_as_np_array(filepath_wav)
        sound = sound[0]
        print(sound.shape)
        print(f"Loaded WAV with sample rate: {sr}")
    except Exception as e:
        return jsonify({'error': f'Failed to load WAV file: {e}'}), 500

    # - Feed that into the Ambient Pipeline
   
    # processed_file_name = 'user_recording_backing.mp3'
    # processed_filepath = os.path.join(UPLOAD_FOLDER, processed_file_name)  # Build the full path for the processed file
    # # processed_audio_file.save(processed_filepath)
    
    
    sound = trim_audio_to_length(sound, sr, duration_in_seconds=MAX_DURATION)
        
    
    
    music, music_sr = ap.audio_to_music(sound, sampling_rate=sr, save_file_loc=processed_filepath)
    
    

    # - Save that audio as an mp3 to the uploads folder (DONE)
    
    
    
    # - Serve that file location to the user (DONE) 

    if os.path.exists(filepath) and os.path.exists(processed_filepath):
        return jsonify({
            'original': updated_filename, #filename,
            'processed': processed_filename #'user_recording_backing.mp3'
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
    app.run(debug=True, port=5001)
