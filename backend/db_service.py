import pymongo
import re
from generate_embedding import EmbeddingOperation

class DatabaseService : 
    def __init__(self, db_name, collection_name) : 
        self.client = pymongo.MongoClient('mongo')
        self.db = db_name
        self.collection = collection_name

    def create_embeddings_for_data(self): 
        eb = EmbeddingOperation()
        database = self.db
        collection = database[self.collection]
        docs = collection.find()
        for doc in docs : 
            if doc["text"]: 
                embedding = eb.embedding_operation(text = doc["text"])
                doc.update_one(
                    {"_id": doc["_id"]}, 
                    {"$set": {"embedding":embedding}}
                )
    
    def insert_drhp_data_to_db(self): 
        database = self.database
        collection = database[self.collection]
        pattern = r'(?m)^(\d+)\s' 
        with open('drhp.md', 'r', encoding='utf-8') as file : 
            text = file.read()
        matches = list(re.finditer(pattern, text))
        for i in range(len(matches)) : 
            start = matches[i].end()
            end = matches[i+1].end if i + 1 < len(matches) else len(text)

            db_text = text[start:end]
            collection.insert_one({
                {"text": db_text}
            })


    

