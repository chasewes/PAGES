# from pydantic import BaseModel, parse_obj_as
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn
from transformers import pipeline
import json
from LLMPromptConstraints import MusicGenInfo
import re 

MODEL_NAME = "meta-llama/Meta-Llama-3-8B" # 'meta-llama/Llama-2-7b-hf' #
HUGGINGFACE_TOKEN = None # "hf_[...]"" # YOUR HF TOKEN HERE

class LLMPromptGenerator:
    def __init__(self, model_name=MODEL_NAME): # device="cpu"
        print('model_name:', model_name)
    
        self.model_name = model_name
        if HUGGINGFACE_TOKEN is None:
            self.hf_pipeline = pipeline('text-generation', model=model_name, device_map='auto', trust_remote_code=True, token=HUGGINGFACE_TOKEN) # device=device)
        else:
            self.hf_pipeline = pipeline('text-generation', model=model_name, device_map='auto', trust_remote_code=True)
        self.info = []
        self.prompts = []
        self.long_term_prompt = None

        self.major_key = None
        self.instrument = None
        
        
    def generate_llm_prompt(self, text, prompt=None):
        
        if prompt is None:
            prompt = """
            TEXT: {} 
            
            TASK: In JSON Format, A piece music generated as background ambience for the above text would have these qualities:
            
        """
        
        #incorporate json format into prompt and return
        return prompt.format(text)
        
    def extract_json_from_llm_output(self, llm_output):
        pattern = r'\{.*?\}'  # Non-greedy match for JSON-like objects
        matches = re.findall(pattern, llm_output, re.DOTALL)

        if not matches:
            return {}  # Return an empty dict if no matches are found

        # Initialize a variable to keep track of the longest JSON match
        longest_match = ""
        for match in matches:
            # Update longest_match if the current match is longer
            if len(match) > len(longest_match):
                try:
                    # Check if the current match is a valid JSON
                    json.loads(match)
                    longest_match = match
                except json.JSONDecodeError:
                    # If not a valid JSON, continue to the next match
                    continue

        # Attempt to parse the longest match as JSON, if it exists
        if longest_match:
            try:
                json_obj = json.loads(longest_match)
                return json_obj
            except json.JSONDecodeError:
                # Should not happen, as we've already tested with json.loads
                return {}
        else:
            return {}  # Return an empty dict if no valid JSON objects were found


    
    def generate_musicgen_prompt(self, text, music_gen_info=MusicGenInfo, prompt=None, flush=False):
        # Generate prompt for the LLM
        llm_prompt = self.generate_llm_prompt(text, prompt=prompt)
        
        #prime the model to generate the proper json format
        parser = JsonSchemaParser(music_gen_info.schema())
        prefix_function = build_transformers_prefix_allowed_tokens_fn(self.hf_pipeline.tokenizer, parser)
        
        #get the output (in json format) from the LLM
        llm_output = self.hf_pipeline(llm_prompt, prefix_allowed_tokens_fn=prefix_function)
        generated_text = llm_output[0]['generated_text']
        
        #extract the json object from the generated_text and convert it to a dict.
        music_attributes = self.extract_json_from_llm_output(generated_text)
        
        
        #set/reset the long term attributes
        if flush or self.major_key is None: 
            self.major_key = music_attributes['is_major_key']
            self.instrument = music_attributes['musical_instrument']

        #create the prompt using fstring
        prompt = (f"Ambient Background music with a {music_attributes['tone']} tone and {music_attributes['intensity']} intensity, "
          f"using {self.instrument} instrumentation to create a {music_attributes['setting']} setting. "
          f"The piece moves at a {music_attributes['tempo']} pace, "
          f"{'in a major key' if self.major_key else 'in a minor key'}, "
          "evoking an immersive atmosphere.")
        
        self.info.append(music_attributes)
        self.prompts.append(prompt)
        
        return prompt
        
    def generate_from_chunks(self, chunks, music_gen_info=MusicGenInfo, prompt=None, **kwargs):
        prompts = []
        durations = []
        
        flush = False
        if 'flush' in kwargs:
            flush = kwargs['flush']
        if 'flush_extractor' in kwargs:
            flush = kwargs['flush_extractor']
            
        if flush:
            self.prompts = []
            self.info = []
        for chunk in chunks: 
            #some logic to determine when to flush could go here. 
            
            #generate the prompt and add it to the list
            prompts.append(self.generate_musicgen_prompt(chunk['text'], music_gen_info=music_gen_info, flush=flush))
            durations.append(float(chunk['duration']))
        
        # self.prompts.extend(prompts)
            
        return prompts, durations
