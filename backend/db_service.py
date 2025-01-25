import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import re
from generate_embedding import EmbeddingOperation

load_dotenv()
class DatabaseService : 
    def __init__(self, db_name, collection_name) : 
        self.client = AsyncIOMotorClient(os.getenv("DB_CONNECTION_STRING"))
        self.db = db_name
        self.collection = collection_name
        self.embedding_instance = EmbeddingOperation()
    
    async def get_all_data(self): 
        database = self.client[self.db]
        collection = database[self.collection]
        docs = collection.find()
        data = []
        async for doc in docs : 
            data.append(doc["text"])
        return data
        
    async def create_embeddings_for_data(self): 
        database = self.client[self.db]
        collection = database[self.collection]
        docs = collection.find()
        async for doc in docs : 
            if doc["text"] and "embedding" not in doc: 
                embedding = self.embedding_instance.embedding_operation(content = doc["text"])
                await collection.update_one(
                    {"_id": doc["_id"]}, 
                    {"$set": {"embedding":embedding}}
                )
    
    async def insert_drhp_data_to_db(self): 
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
            await collection.insert_one({
                "text": db_text
            })
        pattern = r'(?<=####\n)(.*?)(?=\n####)'
        with open('backend/test2.md', 'r', encoding='utf-8') as file:
            content = file.read()
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches : 
            await collection.insert_one({
                "text": match
            })
    
    async def insert_community_summary_into_database(self, collection_name, all_community_data): 
        database = self.client[self.db]
        collection = database[collection_name]
        for community_data in all_community_data:
            await collection.insert_one({
                "community_data": community_data
            })



    

