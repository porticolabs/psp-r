from typing import List, Optional
from pydantic import BaseModel

# Define las clases para pedir recomendaciones y para enviarlas
class Tweet (BaseModel):
    ID : int
    text : str
    user : str
    request : List

class Recommendation (BaseModel):
    originID : str
    text : str
    mediaURL : str
    title : str
    published : str
    author : str