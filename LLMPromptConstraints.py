from pydantic import BaseModel, parse_obj_as, Field, constr

class MusicGenInfo(BaseModel):    
    tone: str
    intensity: str
    setting: str
    tempo: str
    musical_instrument: str
    is_major_key: bool
