from pydantic import BaseModel 

class Answer(BaseModel): 
    question: str