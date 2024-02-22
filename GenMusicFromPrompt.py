from audiocraft.models import MusicGen
from audiocraft.models import MultiBandDiffusion
from audiocraft.utils.notebook import display_audio
import torch

class GenMusicFromPrompt:
    def __init__(self, model_name="facebook/musicgen-large", use_diffusion_decoder=False, previous_song_duration=2, sample_rate=32000, duration=30):
        self.model = MusicGen.from_pretrained(model_name)
        self.mbd = MultiBandDiffusion.get_mbd_musicgen() if use_diffusion_decoder else None
        self.song = None
        self.previous_song_duration = previous_song_duration
        self.sample_rate = sample_rate
        self.duration = duration

    def __call__(self):
        self.display_audio()

    def set_generation_params(self, use_sampling=True, top_k=0, **kwargs):
        duration = self.duration if 'duration' not in kwargs else kwargs['duration']
        self.model.set_generation_params(
            use_sampling=use_sampling,
            top_k=top_k,
            duration=duration
        )
    
    def generate_from_list(self, prompts, **kwargs):
        for prompt in prompts:
            self.generate(prompt, **kwargs)
        return self.song
    
    def generate(self, prompt, **kwargs): # prev_song_duration=2, sample_rate=32000,
        if self.song is None:
            self.generate(prompt)

        
        sample_rate = self.sample_rate if 'sample_rate' not in kwargs else kwargs['sample_rate']
        prev_song_duration = self.previous_song_duration if 'prev_song_duration' not in kwargs else kwargs['prev_song_duration']
        
        
        if 'duration' not in kwargs and self.song is not None:
            kwargs['duration'] = self.duration + prev_song_duration
        
        self.set_generation_params(**kwargs)
        
        # Generate the start of a song
        if self.song is None:
            output = self.model.generate(
                prompt_sample_rate=sample_rate,
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
        combined_song = torch.cat([self.song, continued_song], dim=-1)
        
        self.song = combined_song
        return combined_song

    def display_audio(self):
        if self.song is not None:
            display_audio(self.song)
        else:
            raise ValueError("No song to display. Please generate a song first.")