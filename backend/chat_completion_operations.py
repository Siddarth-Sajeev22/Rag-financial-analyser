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

        system_message = """
            You are an AI assistant that will help in making informed decisions regarding whether or not a given IPO is good fundamentally to buy in the stock market. You will be provided context regarding the IPO from a DRHP document and you will provide information to the user on the basis of the context provided to you only. Do not try to provide any information that is not available from the context
        """
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
