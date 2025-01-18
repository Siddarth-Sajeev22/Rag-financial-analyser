from groq import Groq
from dotenv import load_dotenv
import os 

load_dotenv()

class ChatCompletion : 
    def __init__(self): 
        self.client = Groq(
            api_key = os.getenv("GROQ_API_KEY")
        )
    
    def make_completion_request(self, *args, **kwargs): 
        system_message = kwargs.get("system_message")
        user_message = kwargs.get("user_message")
        completion = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": system_message
                }, 
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        response_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content: 
                response_text += chunk.choices[0].delta.content
        return response_text

    def generate_rag_answer(self, *args, **kwargs):
        df = self.create_df_for_rag()
        system_message = """
            You are an AI assistant that will help in making informed decisions regarding whether or not a given IPO is good fundamentally to buy in the stock market. You will be provided context regarding the IPO from a DRHP document and you will provide information to the user on the basis of the context provided to you only. Do not try to provide any information that is not available from the context
        """

    
    def get_entities_and_relationships_from_chunk(self, chunk): 
        system_message = """You are a financial analyst assistant. Extract key entities and their relationships from the following section of a Draft Red Herring Prospectus (DRHP) of an IPO. Focus on identifying:

                1. **Entities:**
                - Company names
                - Promoters and stakeholders
                - Financial metrics (e.g., revenue, profit, expenses, assets, liabilities)
                - Industry and market details
                - Risks and regulatory compliance
                - Key events (e.g., acquisitions, mergers, partnerships)

                2. **Relationships:**
                - Ownership and stakeholder relations
                - Financial dependencies or impacts (e.g., "Revenue depends on...")
                - Market positioning and competitive relationships
                - Regulatory obligations or dependencies
                - Strategic plans (e.g., "Company plans to expand to...")

                Return the output in a structured format, listing entities first, followed by relationships. Use the following format:

                ### Entities:
                1. Entity Name: [Type of Entity - Company/Person/Metric/Market]
                Description: [Short description]

                ### Relationships:
                1. [Entity A] -> [Relationship Description] -> [Entity B]

                Extract from the following text:
                [Insert chunk of DRHP here]
                """
    
        user_message = chunk
        response = self.make_completion_request(system_message=system_message, user_message=user_message)
        return response 

    def summarize_relationships(self, entities_and_relations): 
        system_message = """ You are a financial analyst assistant. Summarize the following extracted entities and their relationships into a concise, structured format. Ensure the summary highlights the most important details relevant to analyzing a Draft Red Herring Prospectus (DRHP) of an IPO. Focus on:

        1. **Key Entities:**
        - Companies involved
        - Promoters and stakeholders
        - Financial metrics (e.g., revenue, profit, expenses, liabilities, IPO proceeds)
        - Key risks and regulatory factors
        - Strategic initiatives (e.g., expansion plans, debt reduction, acquisitions)

        2. **Key Relationships:**
        - Ownership and stakeholder roles
        - Financial dependencies (e.g., "Revenue depends on...")
        - Market and competitive relationships
        - Strategic dependencies (e.g., "Expansion linked to proceeds from IPO")
        - Risk factors and their impact

        3. **Output Format:**
        - A brief, structured summary highlighting essential entities and relationships.
        - Provide a clear view of the overall financial and strategic position of the company as extracted from the entities and relationships.

        Return the output in the following format:

        **Summary of Entities and Relationships:**

        **Key Entities:**
        - [Entity Name]: [Brief Description]
        - [Entity Name]: [Brief Description]
        ...

        **Key Relationships:**
        - [Entity A] -> [Relationship Description] -> [Entity B]
        - [Entity C] -> [Relationship Description] -> [Entity D]
        ...
        The relationships should always be one is to one. That is [Entity A] -> [Relationship Description] -> [Entity B]. If Entity A has same relationship with multiple entities represent them as two different relationships not within the same relationship
        Summarize the following extracted entities and relationships:
        """

        user_message = entities_and_relations
        response = self.make_completion_request(system_message=system_message, user_message=user_message)
        return response 