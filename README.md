# SQL Agent

Ask questions about a PostgreSQL database in plain English. The FastAPI backend uses Azure OpenAI to generate read only SQL, while the React frontend displays the query and results.

## Setup

Create a `.env` file in the project root:

Install dependencies and start the backend:

```bash
uv sync
uv run uvicorn api:app --reload
```

Start the frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite, usually `http://localhost:5173`.