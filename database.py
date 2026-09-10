import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


def execute_query(sql_query: str):
    with engine.connect() as connection:
        result = connection.execute(text(sql_query))

        rows = result.fetchall()
        columns = result.keys()

        return [
            dict(zip(columns, row))
            for row in rows
        ]