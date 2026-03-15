# Sales AI Agent

A conversational AI agent that lets business analysts explore sales data
using plain English — no SQL knowledge required.

Built with LangChain, Ollama (Llama 3.2), SQLite, and Streamlit.

---

## Demo

Ask questions like:
- "Which product had the highest sales?"
- "Show total sales for the last 5 months"
- "Which customer spent the most?"
- "Show monthly sales trend"
- "Compare sales by region"

The agent understands your question, queries the database automatically,
and replies with a plain English answer and an interactive chart.

---

## Architecture
```
User (plain English)
      ↓
Streamlit Web UI
      ↓
LangChain Agent (Ollama + Llama 3.2)
      ↓
Tools: schema_tool → sql_query_tool
      ↓
SQLite Database (orders, products, customers)
      ↓
Answer + Plotly Chart
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| AI Agent | LangChain + Ollama |
| LLM | Llama 3.2 (runs locally, free) |
| Database | SQLite |
| Charts | Plotly |
| Language | Python 3.11 |

---

## Project Structure
```
sales-ai-agent/
├── app.py            # Streamlit web UI with charts
├── agent.py          # LangChain agent + Ollama LLM
├── tools.py          # Schema and SQL tools
├── db.py             # SQLite connection and queries
├── setup_db.py       # Creates database with sample data
├── test_connection.py# Tests database connection
├── .env              # Environment variables (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.com) installed on your machine

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/sales-ai-agent.git
cd sales-ai-agent
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Pull the AI model
```bash
ollama pull llama3.2
```

### 5. Set up environment variables

Create a `.env` file in the root folder:
```env
OLLAMA_MODEL=llama3.2
```

### 6. Create the database
```bash
python setup_db.py
```

You should see:
```
Database created successfully! sales.db is ready.
```

### 7. Test the connection
```bash
python test_connection.py
```

You should see:
```
Connected! Orders in DB: 18
```

### 8. Run the app
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## How It Works

### Agent loop
```
1. User asks a question in plain English
2. Agent calls schema_tool to understand the database
3. Agent writes a SQL query and calls sql_query_tool
4. SQL result is read and explained in plain English
5. A matching chart is auto-generated
```

### Tools

**schema_tool** — reads the database structure so the agent knows
what tables and columns exist before writing any SQL.

**sql_query_tool** — executes SELECT queries safely. Only SELECT
is allowed — no INSERT, UPDATE, or DELETE.

### Memory

Every tool result is added back into the LLM context window so
the agent can reason across multiple steps before giving a final answer.

---

## Sample Questions

| Question | What the agent does |
|---|---|
| "Show total sales for the last 5 months" | Groups orders by month, sums amounts |
| "Which product had the highest sales?" | Joins orders + products, finds max |
| "Which customer spent the most?" | Joins orders + customers, ranks by total |
| "Show sales by region" | Joins customers, groups by region |
| "Show monthly trend" | Aggregates by month, plots line chart |

---

## Dashboard Features

- 5 live KPI metrics (total revenue, orders, avg order, customers, this month vs last)
- Quick question buttons in the sidebar
- One-click chart buttons for instant visualizations
- Auto-generated charts based on your question type
- Full chat history with charts saved per message

---

## Requirements
```
streamlit
langchain
langchain-community
langchain-ollama
langchain-core
pandas
plotly
python-dotenv
```

---

## Resume / LinkedIn Description

**Sales AI Agent** — Python | LangChain | Ollama | SQLite | Streamlit

Built an end-to-end conversational AI agent that translates plain English
questions into SQL queries, enabling non-technical analysts to explore
sales data without writing SQL. Integrated Ollama (Llama 3.2) as the
local LLM with a custom tool-calling loop for schema inspection and query
execution. Built a Streamlit web UI with live KPI dashboard, chat history,
and auto-generated Plotly charts.

---

## License

MIT License — free to use and modify.
