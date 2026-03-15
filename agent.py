from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from dotenv import load_dotenv
import os
from tools import schema_tool, sql_query_tool

load_dotenv()

SYSTEM_PROMPT = """You are a professional sales data analyst assistant.

The SQLite database has EXACTLY these 3 tables:
- orders (id, product_id, customer_id, quantity, total_amount, order_date)
- products (id, product_name, category, unit_price)
- customers (id, customer_name, region, email)

STRICT RULES:
1. ALWAYS call schema_tool first to confirm table structure.
2. ONLY use table names: orders, products, customers — never invent new tables.
3. For date filtering use: WHERE order_date >= date('now', '-5 months')
4. For monthly grouping use: strftime('%Y-%m', order_date)
5. To get product name: JOIN products p ON o.product_id = p.id
6. To get region: JOIN customers c ON o.customer_id = c.id
7. Never suggest creating tables — they already exist.
8. Only SELECT queries — never INSERT, UPDATE, CREATE or DELETE.
9. Always give a clear plain English answer with actual numbers.
10. Never show raw JSON or tool call syntax in your final answer.

IMPORTANT — SALES MEANS REVENUE:
- When user asks "sales" always use SUM(total_amount) as revenue
- Never use COUNT(*) for sales questions — that gives order count not revenue
- Always show revenue in dollars with $ sign
- Always show both revenue AND order count when showing region/product data

EXAMPLE QUERIES:
- Sales by region:
  SELECT c.region,
         ROUND(SUM(o.total_amount), 2) as revenue,
         COUNT(*) as total_orders
  FROM orders o
  JOIN customers c ON o.customer_id = c.id
  GROUP BY c.region
  ORDER BY revenue DESC

- Sales by product:
  SELECT p.product_name,
         ROUND(SUM(o.total_amount), 2) as revenue,
         COUNT(*) as total_orders
  FROM orders o
  JOIN products p ON o.product_id = p.id
  GROUP BY p.product_name
  ORDER BY revenue DESC

- Top customer:
  SELECT c.customer_name,
         ROUND(SUM(o.total_amount), 2) as revenue
  FROM orders o
  JOIN customers c ON o.customer_id = c.id
  GROUP BY c.customer_name
  ORDER BY revenue DESC
  LIMIT 1

- Last 5 months sales:
  SELECT strftime('%Y-%m', order_date) as month,
         ROUND(SUM(total_amount), 2) as revenue
  FROM orders
  WHERE order_date >= date('now', '-5 months')
  GROUP BY month
  ORDER BY month
"""
TOOLS = {
    "schema_tool": schema_tool,
    "sql_query_tool": sql_query_tool
}

def ask_agent(question: str) -> str:
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        temperature=0,
        base_url="http://localhost:11434"
    )

    llm_with_tools = llm.bind_tools(list(TOOLS.values()))

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question)
    ]

    max_iterations = 8
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            answer = response.content
            if (answer.strip().startswith("{") or
                "sql_query_tool" in answer or
                "schema_tool" in answer):
                messages.append(HumanMessage(
                    content="Please give me only the final plain English answer with actual numbers. No JSON, no code, no tool calls."
                ))
                final = llm_with_tools.invoke(messages)
                return final.content
            return answer

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"Tool: {tool_name} | Args: {tool_args}")
            if tool_name in TOOLS:
                result = TOOLS[tool_name].invoke(tool_args)
            else:
                result = f"Unknown tool: {tool_name}"
            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            ))

    return "I could not complete the analysis. Please try rephrasing your question."