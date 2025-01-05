import pymongo

from backend.generate_embedding import EmbeddingOperation

class DatabaseService : 
    def __init__(self, db_name, collection_name) : 
        self.client = pymongo.connect()
        self.db = db_name
        self.collection = collection_name

    def create_embeddings_for_data(self): 
        eb = EmbeddingOperation()
        for doc in self.collection : 
            if doc["text"]: 
                embedding = eb.embedding_operation(text = doc["text"])
                doc.update_one(
                    {"_id": doc["_id"]}, 
                    {"$set": {"embedding":embedding}}
                )

    

