from fastapi import FastAPI
from fastapi.responses import JSONResponse
from chat_completion_operations import ChatCompletion
from dtos.answer import Answer
from graphrag import GraphRag
from dtos.database_request import DatabaseRequest
from db_service import DatabaseService

graphRag = GraphRag(db_name="standard_glass_lining", collection_name="drhp")
graphRag.initialise_graph_rag_pipeline()
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG Application API"}

@app.post("/query/")
def query_rag(input_text: str):
    # Placeholder logic for RAG functionality
    return {"input": input_text, "response": "This is a mock response."}

@app.post("/enterData")
def enter_data_to_db(db_request: DatabaseRequest):
    db_credentials = db_request.model_dump()
    db_service = DatabaseService(**db_credentials)
    db_service.insert_drhp_data_to_db()
    db_service.create_embeddings_for_data()

@app.post("/answer")
def answer(data: Answer): 
    request = data.model_dump()
    ch = ChatCompletion()
    response = ch.generate_answers_from_communities(graphRag.all_communities_summary, request.question)
    return JSONResponse(response, status_code = 200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
