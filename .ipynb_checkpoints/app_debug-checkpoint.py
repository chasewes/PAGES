import os
from pydub import AudioSegment
# import Ambient_Pipeline as ap
import numpy as np
import tempfile
import torch
import torchaudio
import subprocess


def convert_mp3_to_wav(input_filepath, output_filepath):
    command = ['ffmpeg', '-y','-i', input_filepath, '-ar', '44100', output_filepath]
    subprocess.run(command, check=True)

def load_wav_as_np_array(filepath_wav):
    waveform, sample_rate = torchaudio.load(filepath_wav)
    # Convert the tensor to a numpy array
    np_waveform = waveform.numpy()
    return np_waveform, sample_rate

filename = "balrog_audio.mp3"
filepath = os.path.join('uploads', filename)

filename_wav = "balrog_audio.wav"
filepath_wav = os.path.join('uploads', filename_wav)

try:
    convert_mp3_to_wav(filepath, filepath_wav)
    # Now you can work with the WAV file
except subprocess.CalledProcessError as e:
    print("fricken ffmpeg didn't work")
    
    
    
# Load the WAV file as a NumPy array
try:
    sound, sr = load_wav_as_np_array(filepath_wav)
    print(f"Loaded WAV with sample rate: {sr}")
except Exception as e:
    print("fricken getting the numpy array didn't work")
    
# ambient pipeline stuff goes here. 


