import google.generativeai as genai
import os 
from dotenv import load_dotenv

load_dotenv()

class EmbeddingOperation: 
    def __init__(): 
        genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))

    def embedding_operation(self, *args, **kwargs): 
        content = kwargs.get("content")
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=content,
            task_type="retrieval_document",
            title="Embedding of single string")
        return result 
    