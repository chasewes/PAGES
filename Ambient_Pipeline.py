from LLMPromptGenerator import LLMPromptGenerator#, DetailedInfo
from GenMusicFromPrompt import GenMusicFromPrompt
from LLMPromptConstraints import MusicGenInfo

from audiocraft.models import MusicGen
from audiocraft.models import MultiBandDiffusion
from audiocraft.utils.notebook import display_audio

from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


import math
import torchaudio
import torch
from audiocraft.utils.notebook import display_audio
from tqdm import tqdm
import json
import random

from datasets import load_dataset
from audiocraft.data.audio_utils import convert_audio
import time
import numpy as np
from datasets import Dataset, Audio

import tempfile
import librosa
# from pydub import AudioSegment

import os
import re
# import io

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)


# Parameters for Audio Chunking and Music Duration Generation:
DFLT_CHUNK_LEN_S = 15 # For Whisper
DESIRED_CHUNK_LEN = 15 # For grouping whisper chunks (desired length of a chunk)
MAX_CHUNK_LEN = 20 # For grouping whisper chunks (max length of a chunk)




GROUP_WORD_COUNT = 60 #120 
SONG_DUR_SECONDS = 30 #60 
PREV_SONG_DUR = 2 # 4

MAX_GROUP_CNT = 3

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class Music_Gen_Pipeline():
    
    def __init__(self,
                audio_pipe=None,
                # audio_model=None,
                # audio_processor=None,
                extractor=None,
                generator=None,
                # song_dur_seconds=SONG_DUR_SECONDS,
                # previous_song_duration=PREV_SONG_DUR,
                device="cpu",
                verbose=True,
                desired_section_size=GROUP_WORD_COUNT) -> None:
        # self.audio_model = audio_model
        # self.audio_processor = audio_processor
        self.audio_pipe = audio_pipe
        self.audio_device = 'cpu'
        # self.audio_device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        
        self.extractor = extractor
        self.generator = generator
        
        # self.previous_song_duration = previous_song_duration
        self.device = device
        self.verbose = verbose
        self.desired_section_size = desired_section_size
        
        self.original_audio = None

        if self.extractor is None:
            self.extractor = LLMPromptGenerator() #device=self.device)
            if self.verbose:
                print("Extractor not provided, using default")
        if self.generator is None:
            self.generator = GenMusicFromPrompt(device=self.device)
            if self.verbose:
                print("Generator not provided, using default")
    
    
    def load_txt(self, file_path):
        with open(file_path) as f: 
            book_text = f.read()
        return book_text
                
    def text_to_sections(self, text, desired_section_size=None, max_group_count=None):
        
        # If the input is a file path, load the text from the file
        if os.path.exists(text):
            text = self.load_txt(text)
        
        words = text.split()
        if desired_section_size is None:
            desired_section_size = self.desired_section_size

        # Calculate the total number of words
        total_words = len(words)

        # Determine the number of sections, aiming for equally sized sections
        # Calculate the optimal number of sections to avoid a significantly shorter final section
        optimal_num_sections = round(total_words / desired_section_size)

        # Calculate the new section size to more evenly distribute words across sections
        new_section_size = total_words // optimal_num_sections if total_words % optimal_num_sections == 0 else (total_words // optimal_num_sections) + 1

        # Adjust the last section to avoid being too short
        if total_words % new_section_size < new_section_size / 2:
            optimal_num_sections += 1

        word_sections = [' '.join(words[i:i+new_section_size]) for i in range(0, total_words, new_section_size)]
        
        if max_group_count is not None and len(word_sections) > max_group_count:
            word_sections = word_sections[:max_group_count]
        
        return word_sections
    
    def audio_to_sections(self, wav_audio, default_chunk_length_s=30, desired_lengths=20, max_length=30, last_chunk_buffer=0):
        def group_chunks(chunks, desired_lengths=20, max_length=30):
            def duration(chunk):
                return chunk['timestamp'][1] - chunk['timestamp'][0]
            new_chunks = []
            current_chunk = None
            for chunk in chunks:
                if current_chunk is not None:
                    new_duration = duration(current_chunk) + duration(chunk)
                    
                    if new_duration > max_length:
                        new_chunks.append(current_chunk)
                        current_chunk = None
                    else:
                        current_chunk['timestamp'][1] = chunk['timestamp'][1]
                        current_chunk['duration'] = new_duration
                        current_chunk['text'] += chunk['text']
                        if new_duration > desired_lengths and current_chunk['text'][-1] in ['.', '!', '?', '\n']:
                            new_chunks.append(current_chunk)
                            current_chunk = None
                            continue

                if current_chunk is None:
                    current_chunk = chunk
                    # print(chunk)
                    current_chunk['timestamp'] = list(chunk['timestamp'])
                    current_chunk['duration'] = duration(current_chunk)
                    continue
            if current_chunk is not None:
                new_chunks.append(current_chunk)
            
            total_duration = sum([c['duration'] for c in new_chunks[:-1]])
            new_chunks[-1]['duration'] = ((new_chunks[-1]['timestamp'][1]) - total_duration) + last_chunk_buffer
            
            print('new chunks', new_chunks)
            return new_chunks
        
        print(wav_audio.keys())
        if 'duration' not in wav_audio:
            wav_audio['duration'] = wav_audio['array'].shape[0] / wav_audio['sampling_rate']
            print('duration calculated from array', wav_audio['duration'])
            # wav_audio['duration'] = torchaudio.info(wav_audio['path'])[0].num_frames / wav_audio['sampling_rate']
        
        
        if self.audio_pipe is None:
            self.audio_pipe = 'distil-whisper/distil-large-v2'
        if isinstance(self.audio_pipe, str):
            model_id = self.audio_pipe
            torch_dtype = torch.float16 if torch.cuda.is_available() and self.audio_device != "cpu" else torch.float32
            audio_model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
            audio_model.to(self.audio_device)
            audio_processor = AutoProcessor.from_pretrained(model_id)
            audio_pipe =pipeline(
                "automatic-speech-recognition",
                model=audio_model,
                tokenizer=audio_processor.tokenizer,
                feature_extractor=audio_processor.feature_extractor,
                max_new_tokens=128,
                chunk_length_s=default_chunk_length_s,
                # chunk_length_s=15,
                batch_size=16,
                torch_dtype=torch_dtype,
                device=device,
            )
            self.audio_pipe = audio_pipe
        
        self.original_audio = wav_audio
        
        print('in chunking', wav_audio)
        
        result = self.audio_pipe(wav_audio, return_timestamps=True)
        chunks = result['chunks']
        print(result)
        print(chunks)
        if chunks[-1]['timestamp'][1] is None:
            print('chunck updated')
            new_tuple = (chunks[-1]['timestamp'][0], wav_audio['duration'])
            chunks[-1]['timestamp'] = new_tuple
        chunks = group_chunks(chunks, desired_lengths=desired_lengths, max_length=max_length)
        return chunks, result['text']
        
    def sections_to_prompts(self, word_sections, flush_extractor=False, verbose=None, **kwargs):
        verbose = verbose if verbose is not None else self.verbose
        
        print(word_sections)
        
        # Extract JSON Info
        prompts, durations= self.extractor.generate_from_chunks(word_sections, verbose=verbose, **kwargs)
        
        print(prompts)
        
        return prompts, durations
    
    def prompts_to_music(self, prompts, durations, **kwargs):
        
        music = self.generator.generate_from_list(prompts, durations, **kwargs)
        
        save_file_loc = kwargs.get('save_file_loc', None)
        if save_file_loc is not None:
            if os.path.isdir(save_file_loc):                
                base_name = os.path.basename(save_file_loc).split('.')[0] + '.wav'
                save_file_loc = os.path.join(save_file_loc, base_name)
            self.generator.save_audio(save_file_loc)
    
        
    # def generate_music(self, text, song_dur_seconds=SONG_DUR_SECONDS):
    def audio_to_music(self, wav_audio, song_dur_seconds=SONG_DUR_SECONDS, previous_song_duration=PREV_SONG_DUR, **kwargs):
        # if wav_audio is a np.ndarray (ie. from an mp3 file), "sampling_rate" must be provided in kwargs.
        
        path = None
        if isinstance(wav_audio, str):
            # print('loading from audio not supported yet')
            path = wav_audio
            raise NotImplementedError('loading from audio not supported yet')
            # raise Exception('loading from audio not supported yet')
        # if "is_mp3" in kwargs and kwargs['is_mp3']:
        elif isinstance(wav_audio, np.ndarray):
            if 'sampling_rate' not in kwargs:
                raise ValueError('sampling_rate must be provided for numpy array audio')
            wav_audio = {'path': path, 'array': wav_audio, 'sampling_rate': kwargs['sampling_rate']}
            # 'path', 'array', 'sampling_rate'
              
            # wav_audio = convert_audio(wav_audio, 'wav')
        
        if 'sampling_rate' not in wav_audio:
            if 'sampling_rate' in kwargs:
                wav_audio['sampling_rate'] = kwargs['sampling_rate']
            elif 'sample_rate' in kwargs:
                wav_audio['sampling_rate'] = kwargs['sample_rate']
            else:
                raise ValueError('sampling_rate must be provided in some way')
        
        
        
        # Extract JSON Info
        print("Splitting Audio to chunks")
        chunks, text = self.audio_to_sections(wav_audio, 
                                              default_chunk_length_s=DFLT_CHUNK_LEN_S,
                                              max_length=MAX_CHUNK_LEN,
                                              desired_lengths=DESIRED_CHUNK_LEN)
        
        print("Extracting Info from chunks")
        prompts, durations = self.sections_to_prompts(chunks, **kwargs)
        print(prompts)
        
        save_info_loc = kwargs.get('save_e_info_loc', None)
        if save_info_loc is not None:
            # info_preped = [p.__dict__ for p in info]
            # info_preped = [p.to_dict() for p in self.extractor.info]
            info_preped = self.extractor.info
            
            prepped_output = {'chunks': chunks, 
                              'info': info_preped,
                              'prompts': prompts, 
                              'durations': durations, 
                              }
            
            with open(save_info_loc, 'w') as f:
                # json.dump(info_preped, f)
                json.dump(prepped_output, f)
                
        
        print("Generating Music from prompts")
        
        
        self.prompts_to_music(prompts, durations, **kwargs)
        
        return self.generator.song, self.generator.sample_rate
        


extractor = LLMPromptGenerator()

generator = GenMusicFromPrompt(device=device)

pipe = Music_Gen_Pipeline(extractor=extractor, generator=generator, device=device, verbose=True)



def audio_to_music(audio,**kwargs):
    if 'flush' not in kwargs:
        kwargs['flush'] = True
    song, song_sr = pipe.audio_to_music(audio, **kwargs)
    return song, song_sr

def text_to_music(text, **kwargs):
    print('NOTE: Auto-generated code. Not Tested')
    if 'flush' not in kwargs:
        kwargs['flush'] = True
    sections = pipe.text_to_sections(text, **kwargs)
    prompts, info = pipe.sections_to_prompts(sections, **kwargs)
    pipe.prompts_to_music(info, **kwargs)
    return pipe.generator.song
