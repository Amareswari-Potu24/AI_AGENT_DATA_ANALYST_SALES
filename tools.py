from langchain_core.tools import tool
from db import run_query, get_schema

@tool
def schema_tool(dummy: str = "") -> str:
    """
    Returns all table names and their columns from the sales database.
    ALWAYS call this first before writing any SQL query.
    Use this to understand what tables and columns are available.
    """
    try:
        return get_schema()
    except Exception as e:
        return f"Error fetching schema: {str(e)}"

@tool
def sql_query_tool(query: str) -> str:
    """
    Executes a SQL SELECT query on the sales database and returns results.
    Input must be a valid SELECT statement only.
    Always call schema_tool first to know the table structure.
    """
    query = query.strip().rstrip(";")
    if not query.upper().startswith("SELECT"):
        return "Error: only SELECT queries are allowed."
    try:
        df = run_query(query)
        if df.empty:
            return "Query returned no results."
        return df.to_string(index=False)
    except Exception as e:
        return f"Query failed: {str(e)}"