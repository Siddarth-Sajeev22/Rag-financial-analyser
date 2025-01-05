import os
from dotenv import load_dotenv
import pymongo
import re
from generate_embedding import EmbeddingOperation

load_dotenv()
class DatabaseService : 
    def __init__(self, db_name, collection_name) : 
        self.client = pymongo.MongoClient(os.getenv("DB_CONNECTION_STRING"))
        self.db = db_name
        self.collection = collection_name

    def create_embeddings_for_data(self): 
        eb = EmbeddingOperation()
        database = self.client[self.db]
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
        database = self.client[self.db]
        collection = database[self.collection]
        pattern = r'(?m)^\s*\d+\s' 
        with open('backend/drhp.md', 'r', encoding='utf-8') as file : 
            text = file.read()
        matches = list(re.finditer(pattern, text))
        for i in range(len(matches)) : 
            start = matches[i].end()
            end = matches[i+1].start() if i + 1 < len(matches) else len(text)

            db_text = text[start:end].strip()
            collection.insert_one({
                "text": db_text
            })


    

