from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
import time
import os
import Ambient_Pipeline as ap
import torch
import torchaudio
import tempfile
from pydub import AudioSegment
import io
import numpy as np


app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
def load_audio(input_data):
    """
    Load an audio file from a file path or file-like object, returning the numpy array of samples and the sample rate.
    
    Parameters:
    - input_data: A string representing the file path or a file-like object of the audio file.
    
    Returns:
    - samples: Numpy array of audio samples.
    - sample_rate: Sample rate of the audio file.
    """
    # Check if input_data is a string (file path) or file-like object and load audio accordingly
    if isinstance(input_data, str):
        audio_segment = AudioSegment.from_file(input_data, format="mp3")
    elif isinstance(input_data, io.IOBase):
        audio_segment = AudioSegment.from_file(input_data, format="mp3")
    else:
        raise TypeError("Input must be a file path (string) or a file-like object.")
    
    # Convert to samples
    samples = np.array(audio_segment.get_array_of_samples())
    
    if audio_segment.channels == 2:  # Stereo
        samples = samples.reshape((-1, 2))
    
    samples = samples.astype(np.float32, order='C') / 2**15  # Normalize
    sample_rate = audio_segment.frame_rate
    
    return samples, sample_rate

           
def convert_and_return_audio(music, music_sr):
    # Convert the numpy array to a PyTorch tensor
    # Assuming `music` is 1D numpy array for mono audio
    tensor_audio = torch.tensor(music).unsqueeze(0)  # Add channel dimension if mono

    # Use a temporary file to avoid saving the file permanently
    with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as tmp_file:
        # Save the tensor as an audio file
        torchaudio.save(tmp_file.name, tensor_audio, music_sr)

        # Use Flask's send_file to return the file as part of the response
        # Note: Flask will handle the file sending process, including setting the correct headers.
        response = send_file(
            tmp_file.name,
            mimetype='audio/wav',
            as_attachment=True,
            attachment_filename='output.wav'
        )

        return response

def get_next_file_name(filename, dir_path):
    ind = 0
    if os.path.exists(os.path.join(dir_path, filename)):
        modded_filename = filename.split('.')[0] + f'_{ind}.' + filename.split('.')[1]
        while os.path.exists(os.path.join(dir_path, modded_filename)):
            ind += 1
            modded_filename = filename.split('.')[0] + f'_{ind}.' + filename.split('.')[1]
        return modded_filename
    return filename
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if the post request has the file part
    if 'audioFile' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['audioFile']
    
    # audio_data, sr = ap.load_audio(file)
    
    print(file.filename)
    
    
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        new_filename = get_next_file_name(file.filename, app.config['UPLOAD_FOLDER'])
        file.filename = new_filename
        filename = secure_filename(file.filename)
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        audio_data, sr = load_audio(filepath)
        
        # Simulate processing (in production, replace this with actual processing logic)
        # time.sleep(5)  # Simulate time-consuming processing
        
        music, music_sr = ap.audio_to_music(audio_data, sampling_rate=sr)
        
        
        # CONVERT TO FILE TO BE RETURNED
        
        response = convert_and_return_audio(music, music_sr)
        return response
        
        # Return success message
        # return jsonify({'message': 'File uploaded and processed successfully'}), 200

    return jsonify({'message': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
