import json
import operator
from typing import Any
from dotenv import load_dotenv
from database import execute_query
from langchain_community.tools import tool
from langchain_openai import AzureChatOpenAI
from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage, AIMessageChunk


load_dotenv()


llm = AzureChatOpenAI(
    model="gpt-4.1",
    temperature=0.0,
    streaming=True
)


class MessageState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    database_schema: str
    generated_sql: str
    query_result: Any


def load_schema():

    with open(
        r"D:\Projects\SQL-Agent\schema.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

        database_schema = json.dumps(
            data,
            indent=2
        )

        return database_schema

@tool
def execute_sql(sql_query: str):
    """
    Execute a read-only SQL query against PostgreSQL
    and return the results.
    """

    try:

        sql_query = sql_query.strip()

        if not sql_query.lower().startswith("select"):
            return "Only SELECT queries are allowed."

        results = execute_query(sql_query)

        return results

    except Exception as e:

        return f"SQL execution error: {str(e)}"



@tool
def analysis_user_question(
    user_question: str,
    database_schema: str
):
    """
    Analyze the user's question and generate
    a valid SQL query based on the database schema.
    """

    system_prompt = """
            You are a PostgreSQL SQL query generator.

            Generate a SQL query for the user's question using ONLY the
            provided database schema.

            STRICT RULES:
            - Use table and column names EXACTLY as they appear in the schema.
            - Never rename, guess, or invent tables or columns.
            - Verify every column against the provided schema before using it.
            - Generate only SELECT queries.
            - Do not add unnecessary filters or conditions.
            - Only apply conditions explicitly required by the user's question.
            - Do not assume relationships that are not present in the schema.
            - Return ONLY the SQL query.
            - Do not use markdown.
            - Do not provide explanations.
        """
    message = [

        {
            "role": "system",
            "content": system_prompt
        },

        {
            "role": "user",
            "content": f"""
                User Question:
                {user_question}

                Database Schema:
                {database_schema}

                Important:
                Use the EXACT table and column names from the schema above.
            """
        }
    ]

    result = llm.invoke(message)

    return result.content


tools = [analysis_user_question]
tools_by_name = {
    tool.name: tool
    for tool in tools
}
model_with_tools = llm.bind_tools(tools)



def llm_call(state: MessageState):

    system_prompt = """
        You are a SQL expert and database assistant.

        Your job is to determine whether the user's question
        is related to the database.

        Rules:

        1. If the question is related to the database:
        - Call the analysis_user_question tool.
        - Do not answer the question yourself.
        - Do not generate SQL yourself.

        2. If the question is not related to the database:
        - Do not call any tool.
        - Return exactly:
            This question is outside the scope of the database.

        3. Never invent database information.
    """

    response = model_with_tools.invoke(
        [
            SystemMessage(content=system_prompt),
            *state["messages"]
        ]
    )

    return {
        "messages": [response]
    }


def tool_node(state: MessageState):

    last_message = state["messages"][-1]

    if not isinstance(last_message, AIMessage):

        return {
            "messages": []
        }


    # Find latest user question
    latest_user_question = next(
        (
            message.content
            for message in reversed(state["messages"])
            if isinstance(message, HumanMessage)
        ),
        ""
    )

    for tool_call in last_message.tool_calls:

        tool_name = tool_call["name"]

        if tool_name == "analysis_user_question":

            sql_query = analysis_user_question.invoke(
                {
                    "user_question": latest_user_question,
                    "database_schema": state["database_schema"]
                }
            )

            sql_query = str(sql_query).strip()


            # Remove markdown code fences if LLM returns them
            if sql_query.startswith("```sql"):

                sql_query = sql_query[6:]

            elif sql_query.startswith("```"):

                sql_query = sql_query[3:]


            if sql_query.endswith("```"):

                sql_query = sql_query[:-3]


            sql_query = sql_query.strip()


            print("\n\nGenerated SQL:")
            print(sql_query)

            results = execute_sql.invoke(
                {
                    "sql_query": sql_query
                }
            )


            return {
                "generated_sql": sql_query,
                "query_result": results,
                "messages": []
            }


    return {
        "messages": []
    }

def should_continue(state: MessageState):

    last_message = state["messages"][-1]


    if isinstance(last_message, AIMessage):

        if last_message.tool_calls:

            return "tool_node"


    return END


agent_builder = StateGraph(MessageState)

agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_edge(START, "llm_call")

agent_builder.add_conditional_edges(
"llm_call",
    should_continue
)

agent_builder.add_edge(
    "tool_node",
    END
)

agent = agent_builder.compile()