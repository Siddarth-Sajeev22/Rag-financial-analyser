from pydantic import BaseModel 

class DatabaseRequest(BaseModel): 
    db_name : str
    collection_name : str