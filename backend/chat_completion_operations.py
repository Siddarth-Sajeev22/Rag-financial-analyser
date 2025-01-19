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

    def generate_answers_from_communities(self, community_summaries, query):
        intermediate_answers = []
        for index, summary in enumerate(community_summaries):
            print(f"Summary index {index} of {len(community_summaries)}:")
            system_message = "Answer the following query based on the provided summary."
            user_message = f"Query: {query} Summary: {summary}"
            response = self.make_completion_request(system_message, user_message)
            print("Intermediate answer:", response)
            intermediate_answers.append(response)
        system_message = "Combine these answers into a final, concise response."
        user_message = f"Intermediate answers: {intermediate_answers}"
        final_response = self.make_completion_request(system_message, user_message)
        return final_response

    
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
    
    def summarize_communites(self, description): 
        system_message = """ You are an expert in analyzing and summarizing data graphs. Your task is to summarize communities of entities and their relationships in a graph. For each community, provide a meaningful description, including key entities, their roles, the primary relationships between them, and any notable insights.
        """

        user_message = f"""The following is a description of a community extracted from a graph:\n\n{description}\n\n.Please summarize this community, highlighting its key entities, relationships and significance."""
        
        response = self.make_completion_request(system_message=system_message, user_message=user_message)
        return response 