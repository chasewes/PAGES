from pydantic import BaseModel, parse_obj_as
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn
from transformers import pipeline
import json

"""
NOTE: IF WANT TO CHANGE MUSIC PROMPT LOOK FOR **MUSIC_PROMPT** IN THE CODE
Short term attributes and long term attributes are captured for every text chunk passed in
flush attribute empties stored info and long_term_prompt
long term attributes is collected from the first text chunk passed in and is used as a prefix for all the short term attributes
short term attributes used in the prompt for a given chunk
"""


class DetailedInfo():
    def __init__(self, text, info, prompt=None): #, info, prompt, duration=None, timestamps=None):
        if isinstance(text, dict):
            self.text = text['text']
            self.duration = text['duration']
            self.timestamps = text['timestamp']
        else:
            self.text = text
            self.duration = None
            self.timestamps = None
        # self.info = info
        self.short_term = info.short_term if info is not None else None
        self.long_term = info.long_term if info is not None else None
        self.prompt = prompt

    def __call__(self):
        return self.prompt
    
    def to_dict(self):
        return {
            "text": self.text,
            "duration": self.duration,
            "timestamps": self.timestamps,
            "short_term": self.short_term.__dict__ if self.short_term is not None else None,
            "long_term": self.long_term.__dict__ if self.long_term is not None else None,
            "prompt": self.prompt
        }
    
    

class MusicGenInfo(BaseModel):
    class ShortTermAttributes(BaseModel):
        """
        Attributes that are collected for every text chunk passed in
        Note: the variable name influences what the LLM attempts to extract
        """
        tone: str
        intensity: str
        is_crescendo: bool
        volume: str
        
        def __str__(self):
            # **MUSIC_PROMPT**
            # formatting for the short term attribute prompt
            ret = [f"{self.tone} tone",
                   f"{self.intensity} intensity",
                   f"and {self.volume} volume",
                #    "with a crescendo" if self.is_crescendo else "with no crescendo"
                   ]
            ret = " ".join(ret)
            return ret
        
    class LongTermAttributes(BaseModel):
        """
        Attributes that are collected from the first text chunk passed in and is used as a prefix for all the short term attributes
        Technically these are collected for all chunks, but only the first chunk's attributes are used in prompts
        Note: the variable name influences what the LLM attempts to extract
        """
        instrumentation: str
        # short_ambient_music_setting: str
        # short_music_genre_setting: str
        # short_music_setting: str
        short_background_ambient_setting: str
        short_music_descriptors: str
        pitch: str
        beat: str
        is_major_key: bool
            
    
        def __str__(self):
            # **MUSIC_PROMPT**
            # Formatting for the long term attribute prefix
            ret = [
            # f"Ambient music with",
            # f"{self.short_music_setting} ambient music setting",
            f"{self.short_background_ambient_setting} ambient music setting",
            f"{self.instrumentation} instrumentals",
            # f"({self.short_music_descriptors})",
            # f"{self.pitch} pitch",
            # f"{self.beat} beat",
            "in a major key." if self.is_major_key else "in a minor key."
            ]
            ret = " ".join(ret)
            return ret
    short_term: ShortTermAttributes
    long_term: LongTermAttributes
        
class LLMPromptGenerator:
    def __init__(self, model_name="TheBloke/Llama-2-7b-Chat-GPTQ", music_gen_info=MusicGenInfo, prompt=None): # device="cpu"
        self.model_name = model_name
        self.hf_pipeline = pipeline('text-generation', model=model_name, device_map='auto') # device=device)
        self.info = []
        self.long_term_prompt = None
        self.music_gen_info = music_gen_info #MusicGenInfo
        self.prompt = prompt
        
    def generate_llm_prompt(self, text, music_gen_info=None, prompt=None):
        if music_gen_info is None:
            music_gen_info = self.music_gen_info
        if prompt is not None:
            self.prompt = prompt
        elif self.prompt is None:
            self.prompt = """
        {}\n\n In the following format {}, A piece music generated as background ambience for the above text would have these qualities: \n
        """
        
        # NOTE: Prompt expects two input locations for formatting purposes.
        if isinstance(text, list):
            return [self.generate_llm_prompt(t, prompt=prompt) for t in text]
        
        # if prompt is None:
            
        prompt = self.prompt.format(text, self.music_gen_info.schema_json())
        
        
        # prompt = f"""
        # {text}\n\n In the following format {music_gen_info.schema_json()}, A piece music generated as background ambience for the above text would have these qualities: \n
        # """
        return prompt
    
    def extract_info(self, text, music_gen_info=None, prompt=None, flush=False):
        if music_gen_info is not None:
            self.music_gen_info = music_gen_info
            
        ret_first = False
        
        if not isinstance(text, list):
            text = [text]
            ret_first = True
        if len(text) == 0:
            return
        
        text_raw = text
        # durations = [None for t in text]
        # timestamps = [None for t in text]
        
        if isinstance(text[0], dict):
            text_raw = [t['text'] for t in text]
            # durations = [t['duration'] for t in text]
            # timestamps = [t['timestamp'] for t in text]
        
        
        llm_prompts = self.generate_llm_prompt(text_raw, prompt=prompt) # music_gen_info
        parser = JsonSchemaParser(self.music_gen_info.schema())
        prefix_function = build_transformers_prefix_allowed_tokens_fn(self.hf_pipeline.tokenizer, parser)
        output_dict = self.hf_pipeline(llm_prompts, prefix_allowed_tokens_fn=prefix_function)
        
        if flush: # Empties the info list and long_term_prompt
            self.info = []
            self.long_term_prompt = None
            
        results = []
        # if isinstance(text, list):
        for i, p in enumerate(llm_prompts):
            results.append(json.loads(output_dict[i][0]['generated_text'][len(p):]))
            
        info_formatted = parse_obj_as(list[self.music_gen_info], [r for r in results])
        info_detailed = [DetailedInfo(t, i) for t, i in zip(text, info_formatted)]
        
        self.info.extend(info_detailed)
        
        if ret_first:
            return results[0]
        
        return results
        # result = json.loads(output_dict[0]['generated_text'][len(llm_prompts):])
        # self.info.append(parse_obj_as(MusicGenInfo, result))
        # return result

    def prompts(self):
        if self.long_term_prompt is None:
            self.long_term_prompt = str(self.info[0].long_term)
        
        prompts = []
        for i in self.info:
            # **MUSIC_PROMPT**
            # Combining the long and short term portions
            new_prompt = f"{self.long_term_prompt} {str(i.short_term)}"
            i.prompt = new_prompt
            prompts.append(new_prompt)
        
        
        return prompts, self.info
