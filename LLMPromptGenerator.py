from pydantic import BaseModel, parse_obj_as
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn
from transformers import pipeline
import json


class MusicGenInfo(BaseModel):
    class ShortTermAttributes(BaseModel):
        tone: str
        intensity: str
        is_crescendo: bool
        volume: str
        
        def __str__(self):
            # return f"{self.tone} {self.intensity} {self.volume} {self.is_crescendo}"
            ret = [f"{self.tone} tone",
                   f"{self.intensity} intensity",
                   f"and {self.volume} volume",
                #    "with a crescendo" if self.is_crescendo else "with no crescendo"
                   ]
            ret = " ".join(ret)
            return ret
        
    class LongTermAttributes(BaseModel):
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
    def __init__(self, model_name="TheBloke/Llama-2-7b-Chat-GPTQ"): # device="cpu"
        self.model_name = model_name
        self.hf_pipeline = pipeline('text-generation', model=model_name, device_map='auto') # device=device)
        self.info = []
        self.long_term_prompt = None
        
    def generate_prompt(self, text, music_gen_info=MusicGenInfo):
        if isinstance(text, list):
            return [self.generate_prompt(t, music_gen_info) for t in text]
        
        prompt = f"""
        {text}\n\n In the following format {music_gen_info.schema_json()}, A piece music generated as background ambience for the above text would have these qualities: \n
        """
        return prompt
    
    def extract_info(self, text, music_gen_info=MusicGenInfo, flush=False):
        prompts = self.generate_prompt(text, music_gen_info)
        parser = JsonSchemaParser(music_gen_info.schema())
        prefix_function = build_transformers_prefix_allowed_tokens_fn(self.hf_pipeline.tokenizer, parser)
        output_dict = self.hf_pipeline(prompts, prefix_allowed_tokens_fn=prefix_function)
        
        if flush: # Empties the info list and long_term_prompt
            self.info = []
            self.long_term_prompt = None
            
        results = []
        if isinstance(text, list):
            for i, p in enumerate(prompts):
                results.append(json.loads(output_dict[i][0]['generated_text'][len(p):]))
            self.info.extend(parse_obj_as(list[MusicGenInfo], [r for r in results]))
            return results
        result = json.loads(output_dict[0]['generated_text'][len(prompts):])
        self.info.append(parse_obj_as(MusicGenInfo, result))
        return result

    def prompts(self):
        if self.long_term_prompt is None:
            self.long_term_prompt = str(self.info[0].long_term)
        
        prompts = []
        for i in self.info:
            prompts.append(f"{self.long_term_prompt} {str(i.short_term)}")
        
        return prompts
