from fastapi import FastAPI
from dtos.database_request import DatabaseRequest
from db_service import DatabaseService

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
