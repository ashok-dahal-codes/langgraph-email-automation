import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from src.graph import Workflow
from dotenv import load_dotenv

# Load .env file
load_dotenv()


app = FastAPI(
    title="Gmail Automation",
    version="1.0",
    description="LangGraph backend for the AI Gmail automation workflow",
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

def get_runnable():
    return Workflow().app.with_config({"recursion_limit": 1000})

# Use the same graph step limit as the command-line runner
runnable = get_runnable()

# Create the Fast API route to invoke the runnable
add_routes(app, runnable)

def main():
    # LangServe prints Unicode symbols; use UTF-8 on Windows too.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    # Start the API
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
