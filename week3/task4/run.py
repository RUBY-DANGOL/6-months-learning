"""Run the SQL Agent FastAPI server."""
import uvicorn

if __name__ == "__main__":
    print("SQL Agent API running at http://127.0.0.1:8000")
    print("Open in browser to use the web form, or POST /agent/sql")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
