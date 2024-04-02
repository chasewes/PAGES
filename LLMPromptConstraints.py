from pydantic import BaseModel, parse_obj_as, Field, constr

category_list = ["Dazzling",
"Dark",
"Awe-inspiring",
"Creepy",
"Complicated",
"Amusing",
"Addictive",
"Witty",
"Unique",
"Unexpected",
"Gripping",
"Astonishing"]
category_list = '|'.join(category_list)


genres = ["Fantasy",
"Adventure",
"Romance",
"Contemporary",
"Dystopian",
"Mystery",
"Horror",
"Thriller",
"Paranormal",
"Historical fiction",
"Science Fiction",
"Childrens"]
genres = '|'.join(genres)


feelings = ["love", "joy", "surprise", "anger", "sadness", "fear"]
feelings = '|'.join(feelings)


class MusicGenInfoModded(BaseModel):
    class ShortTermAttributes(BaseModel):
        """
        Attributes that are collected for every text chunk passed in
        Note: the variable name influences what the LLM attempts to extract
        """
        # tone: str
        # intensity: str
        # is_crescendo: bool
        # volume: str
        
        # genre: str
        one_sentence_description: str
        music_setting: str
        feeling: constr(pattern=feelings)
        is_setting_described: bool
        setting_description: str
        one_sentence_soundscape: str
        
        def __call__(self):
            return vars(self)
        
        def __str__(self):
            # **MUSIC_PROMPT**
            # formatting for the short term attribute prompt
            # ret = [f"{self.tone} tone",
            #        f"{self.intensity} intensity",
            #        f"and {self.volume} volume",
            #     #    "with a crescendo" if self.is_crescendo else "with no crescendo"
            #        ]
            # ret = " ".join(ret)
            ret = str(vars(self))
            
            ret = [
                f'{self.one_sentence_soundscape}',
                f'Invoking a feeling of {self.feeling}']
            ret = " ".join(ret)
            
            
            return ret
        
    class LongTermAttributes(BaseModel):
        """
        Attributes that are collected from the first text chunk passed in and is used as a prefix for all the short term attributes
        Technically these are collected for all chunks, but only the first chunk's attributes are used in prompts
        Note: the variable name influences what the LLM attempts to extract
        """
        instruments: str
        # short_ambient_music_setting: str
        # short_music_genre_setting: str
        # short_music_setting: str
        # short_background_ambient_setting: str
        # short_music_descriptors: str
        # pitch: str
        # beat: str
        # is_major_key: bool
        book_genre: constr(pattern=genres)
        # sentiment: str
        music_type: str
        # categories: ['Dark', 'Dazzling', 'Other']
        # categories: constr(regex='^(Dark|Dazzling|Other)$')
        # categories: constr(pattern=r'(Dark|Dazzling|Other)')
        descriptor: constr(pattern=category_list)
        one_sentence_soundscape: str
        
        def __call__(self):
            return vars(self)
        # is_mystical: bool
    
        def __str__(self):
            # **MUSIC_PROMPT**
            # Formatting for the long term attribute prefix
            # ret = [
            # # f"Ambient music with",
            # # f"{self.short_music_setting} ambient music setting",
            # f"{self.short_background_ambient_setting} ambient music setting",
            # f"{self.instrumentation} instrumentals",
            # # f"({self.short_music_descriptors})",
            # # f"{self.pitch} pitch",
            # # f"{self.beat} beat",
            # "in a major key." if self.is_major_key else "in a minor key."
            # ]
            # ret = " ".join(ret)
            
            ret = str(vars(self))
            ret = [
                ''
                # f'{self.one_sentence_soundscape}'
                f'{self.descriptor}',
                f'{self.book_genre}',
                f'{self.music_type}'
                
                # f'{self.instruments}']
            ]
            ret = " ".join(ret)
            
            
            return ret
    short_term: ShortTermAttributes
    long_term: LongTermAttributes
    
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
    
    def __str__(self):
        text = f'long:{self.long_term()}, short:{self.short_term()}'
        return text
    
prompt = """
    {}\n\n In this format {}, describe this book as it relates to these categories. Be creative and use interesting words.
    """
    
music_gen_info = MusicGenInfoModded
