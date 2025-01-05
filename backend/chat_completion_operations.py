from groq import Groq
from dotenv import load_dotenv
import os 

load_dotenv()

class ChatCompletion : 
    def __init__(self): 
        self.client = Groq(
            api_key = os.getenv("GROQ_API_KEY")
        )
    def generate_rag_answer(self, *args, **kwargs):
        completion = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a financial advisor that can provide accurate information based on information preseented to you on different ipos"
                }, 
                {
                    "role": "user", 
                    "content": "How do i know whether to buy a stock or not "
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        for chunk in completion:
            print(chunk.choices[0].delta.content or "", end="")
