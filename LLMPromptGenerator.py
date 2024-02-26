from pydantic import BaseModel
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn
from transformers import pipeline

class LLMPromptGenerator:
    
    class MusicGenInfo(BaseModel):
        tone: str
        intensity: str
        instrumentation: str
        setting: str
        scene_description: str
        pitch: str
        crescendo: bool
        # device: str

    def __init__(self, model_name="TheBloke/Llama-2-7b-Chat-GPTQ"): # device="cpu"
        # self.device = device
        self.model_name = model_name
        self.hf_pipeline = pipeline('text-generation', model=model_name, device_map='auto') # device=device)
        
        
    def generate_prompt(self, text, music_gen_info=MusicGenInfo):
        if isinstance(text, list):
            return [self.generate_prompt(t, music_gen_info) for t in text]
        prompt = f"""
        {text}\n\n In the following format {music_gen_info.schema_json()}, A piece music generated as background ambience for the above text would have these qualities: \n
        """
        return prompt
    
    def extract_info(self, text, music_gen_info=MusicGenInfo):
        prompt = self.generate_prompt(text, music_gen_info)
        parser = JsonSchemaParser(music_gen_info.schema())
        prefix_function = build_transformers_prefix_allowed_tokens_fn(self.hf_pipeline.tokenizer, parser)
        output_dict = self.hf_pipeline(prompt, prefix_allowed_tokens_fn=prefix_function)
        results = []
        # print(len(output_dict))
        # print(len(output_dict[0]))
        if isinstance(text, list):
            for i, p in enumerate(prompt):
                results.append(output_dict[i][0]['generated_text'][len(p):])
            return results
        result = output_dict[0]['generated_text'][len(prompt):]
        return result
    