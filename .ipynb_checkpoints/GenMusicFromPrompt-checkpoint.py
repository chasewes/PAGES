from audiocraft.models import MusicGen
from audiocraft.models import MultiBandDiffusion
from audiocraft.utils.notebook import display_audio

class GenMusicFromPrompt:
    def __init__(self, model_name="facebook/musicgen-large", use_diffusion_decoder=False):
        self.model = MusicGen.from_pretrained(model_name)
        self.mbd = MultiBandDiffusion.get_mbd_musicgen() if use_diffusion_decoder else None
        self.song = None

    def __call__():
        self.display_audio()

    def set_generation_params(self, use_sampling=True, top_k=0, duration=60):
        self.model.set_generation_params(
            use_sampling=use_sampling,
            top_k=top_k,
            duration=duration
        )
    
    def generate(self, prompt, **kwargs):
        self.set_generation_params(**kwargs)

        output = model.generate(
            descriptions=[
                prompt
            ],
            progress=True, return_tokens=True
        )
        initial_song = output[0]

        self.song = initial_song
    
    def generate_continuation(self, prompt, prev_song_duration=2, sample_rate=32000, **kwargs):
        if self.song is None:
            self.generate(prompt)

        self.set_generation_params(**kwargs)

        # Get the last `prev_song_duration` seconds of the previous song
        prompt_waveform = self.song[..., -int(prev_song_duration * sample_rate):]

        # Generate the continuation
        continued_song = model.generate_continuation(prompt_waveform,  # Add batch dimension
                                            prompt_sample_rate=sample_rate,  # Use the generated sample rate
                                            progress=True, return_tokens=True, descriptions=[prompt])

    def display_audio(self):
        if self.song is not None:
            display_audio(self.song)
        else:
            raise ValueError("No song to display. Please generate a song first.")