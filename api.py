from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.messages import HumanMessage

from main import agent, load_schema,MessageState

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query_database(request: QueryRequest):

    schema = load_schema()

    state: MessageState = {
        "messages": [
            HumanMessage(content=request.question)
        ],
        "database_schema": schema,
        "generated_sql": "",
        "query_result": None
    }

    result = agent.invoke(state)

    return {
        "sql": result.get("generated_sql", ""),
        "result": result.get("query_result"),
    }