import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse

from app.agent import process_question
from app.models import AgentRequest, AgentResponse
from app.logger import ensure_log_dir

app = FastAPI(
    title="SQL Agent API",
    description="Converts natural language to PostgreSQL SELECT queries and executes them.",
    version="1.0.0",
)


@app.on_event("startup")
async def startup():
    ensure_log_dir()


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
<!DOCTYPE html>
<html>
<head><title>SQL Agent API</title></head>
<body style="font-family:sans-serif;max-width:700px;margin:40px auto;padding:20px">
<h1>SQL Agent API</h1>
<p>Convert natural language to PostgreSQL queries and execute them.</p>
<h2>Try it</h2>
<form action="/agent/sql" method="get">
  <input name="question" size="60" placeholder="e.g. Count customers per country">
  <button type="submit">Run</button>
</form>
<h2>Examples</h2>
<ul>
  <li><a href="/agent/sql?question=Count customers per country">Count customers per country</a></li>
  <li><a href="/agent/sql?question=How many shipped orders are from USA customers">Shipped orders from USA</a></li>
  <li><a href="/agent/sql?question=List all products">List all products</a></li>
  <li><a href="/agent/sql?question=Find customers in France">Find customers in France</a></li>
  <li><a href="/agent/sql?question=What is the total amount of payments received">Total payments received</a></li>
  <li><a href="/agent/sql?question=How many products are in each product line">Products per product line</a></li>
  <li><a href="/agent/sql?question=Get employees with office city">Employees with office city</a></li>
  <li><a href="/agent/sql?question=Show all orders from customers in Germany">Orders from Germany</a></li>
</ul>
<h3>CLI example</h3>
<pre>curl -X POST http://127.0.0.1:8000/agent/sql -H "Content-Type: application/json" -d '{"question": "Count customers per country"}'</pre>
</body>
</html>
    """


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sql-agent"}


@app.api_route("/agent/sql", methods=["GET", "POST"])
async def agent_sql(request: Request, question: str = ""):
    if request.method == "POST":
        body = await request.json()
        question = body.get("question", "")
    result = process_question(question)

    if request.method == "GET" and request.headers.get("accept", "").startswith("text/html"):
        html = _render_html(question, result)
        return HTMLResponse(content=html)

    return AgentResponse(
        sql=result.get("sql", ""),
        result=result.get("result"),
        summary=result.get("summary", ""),
        status=result.get("status", "error"),
        error=result.get("error"),
        execution_time=result.get("execution_time"),
        retries=result.get("retries", 0),
    )


@app.post("/agent/sql/raw")
async def agent_sql_raw(request: Request):
    body = await request.json()
    question = body.get("question", "")
    result = process_question(question)
    return JSONResponse(content=result)


def _render_html(question: str, result: dict) -> str:
    rows = result.get("result") or []
    row_html = ""
    for r in rows:
        escaped = str(r).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        row_html += f"<tr><td style='border:1px solid #ccc;padding:4px'>{escaped}</td></tr>"

    return f"""
<!DOCTYPE html>
<html>
<head><title>SQL Agent — Result</title></head>
<body style="font-family:sans-serif;max-width:800px;margin:40px auto;padding:20px">
<h1>SQL Agent</h1>
<form action="/agent/sql" method="get">
  <input name="question" size="60" value="{question.replace('"', '&quot;')}">
  <button type="submit">Run</button>
</form>
<hr>
<h2>Result</h2>
<p><strong>Status:</strong> {result.get("status")}</p>
<p><strong>Summary:</strong> {result.get("summary")}</p>
<p><strong>SQL:</strong></p>
<pre style="background:#f4f4f4;padding:10px;border-radius:4px">{result.get("sql", "")}</pre>
<p><strong>Execution time:</strong> {result.get("execution_time", "-")}s | <strong>Retries:</strong> {result.get("retries", 0)}</p>
<h3>Rows ({len(rows)})</h3>
<table style="border-collapse:collapse;width:100%">
{row_html}
</table>
<p><a href="/">Back</a></p>
</body>
</html>
    """
