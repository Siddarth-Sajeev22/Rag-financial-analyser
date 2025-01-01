from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG Application API"}

@app.post("/query/")
def query_rag(input_text: str):
    # Placeholder logic for RAG functionality
    return {"input": input_text, "response": "This is a mock response."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
