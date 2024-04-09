from audiocraft.models import MusicGen
from audiocraft.models import MultiBandDiffusion
from audiocraft.utils.notebook import display_audio
import torchaudio
import torch
from tqdm import tqdm

# 'flush' will remove cached song while using the end of the song as input to generate the next part

class GenMusicFromPrompt:
    def __init__(self, model_name="facebook/musicgen-large", use_diffusion_decoder=False, previous_song_duration=2, sample_rate=32000, duration=30, device="cpu"):
        # self.model = MusicGen.from_pretrained(model_name)
        print('Device', device)
        self.model = MusicGen.get_pretrained(model_name, device=device)
        self.mbd = MultiBandDiffusion.get_mbd_musicgen() if use_diffusion_decoder else None
        self.song = None
        self.previous_song_duration = previous_song_duration
        self.sample_rate = sample_rate
        self.duration = duration
        self.device = device

    # def __call__(self):
    #     self.display_audio()

    def set_generation_params(self, use_sampling=True, top_k=0, **kwargs):
        duration = self.duration if 'duration' not in kwargs else kwargs['duration']
        self.model.set_generation_params(
            use_sampling=use_sampling,
            top_k=top_k,
            duration=duration
        )
    
    def generate_from_list(self, prompts, durations, verbose=False, **kwargs):
        # If want to start a new song pass in song=None
        # If want to continue from the previous song pass in song=<wav_form_ndarray>
        for index in tqdm(range(len(prompts))):
            prompt = prompts[index]
            curr_duration = durations[index]
            
            curr_kwargs = kwargs.copy()

            curr_kwargs['duration'] = curr_duration
            self.generate(prompt, **curr_kwargs)
            
            if 'song' in kwargs:
                del kwargs['song']
            if 'flush' in kwargs:
                del kwargs['flush']
                # kwargs['song'] = self.song
        return self.song
    
    def generate(self, prompt, **kwargs): # prev_song_duration=2, sample_rate=32000,
        # If want to start a new song pass in song=None
        # If want to continue from the previous song pass in song=<wav_form_ndarray>
        
        
        sample_rate = self.sample_rate if 'sample_rate' not in kwargs else kwargs['sample_rate']
        prev_song_duration = self.previous_song_duration if 'prev_song_duration' not in kwargs else kwargs['prev_song_duration']
        
        # if 'duration' not in kwargs and self.song is not None:
        #     new_duration = self.duration if 'song_duration' not in kwargs else kwargs['song_duration']
            
        #     kwargs['duration'] = new_duration + prev_song_duration
        # elif self.song is None and 'song_duration' in kwargs:
        #     kwargs['duration'] = kwargs['song_duration']
        
        if 'duration' not in kwargs:
            kwargs['duration'] = self.duration
        if self.song is not None:
            kwargs['duration'] = kwargs['duration'] + prev_song_duration 
        
        self.set_generation_params(**kwargs)
        
        if 'song' in kwargs:
            self.song = kwargs['song']
        
        # Generate the start of a song
        if self.song is None:
            output = self.model.generate(
                # prompt_sample_rate=sample_rate,
                progress=True, return_tokens=True, descriptions=[prompt]
            )
            initial_song = output[0]
            self.song = initial_song
            return initial_song
            
        # Generating Continuation:
        # Get the last `prev_song_duration` seconds of the previous song
        trim_amount = int(prev_song_duration * sample_rate)
        prompt_waveform = self.song[..., -trim_amount:]

        # Generate the continuation
        continued_song = self.model.generate_continuation(prompt_waveform,  # Add batch dimension
                                            prompt_sample_rate=sample_rate,  # Use the generated sample rate
                                            progress=True, return_tokens=True, descriptions=[prompt])
        continued_song = continued_song[0][:, :, trim_amount:]
        
        if 'flush' in kwargs and kwargs['flush']:
            self.song = continued_song
            return continued_song
        
        combined_song = torch.cat([self.song, continued_song], dim=-1)
        
        self.song = combined_song
        return combined_song

    def display_audio(self, song=None):
        if song is None:
            song = self.song.to('cpu')
            
        if song is not None:
            display_audio(self.song, self.sample_rate)
        else:
            raise ValueError("No song to display. Please generate a song first.")
        
    def save_audio(self, filename, song=None):
        if song is None:
            song = self.song.to('cpu')#.numpy()
            
        if song is not None:
            if song.ndim == 3:
                song = song.squeeze(0)
            
            torchaudio.save(filename, song, self.sample_rate)
            print(f"Saved song to {filename}")
        else:
            raise ValueError("No song to save. Please generate a song first.")