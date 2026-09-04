"""Check configuration and API access without reading or modifying email."""
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from src.config import PROJECT_ROOT, GROQ_MODEL, EMBEDDING_MODEL, VECTORSTORE_DIR


def main():
    problems = []
    for name in ("MY_EMAIL", "GROQ_API_KEY", "GOOGLE_API_KEY"):
        present = bool(os.getenv(name, "").strip())
        print(f"{name}: {'configured (hidden)' if present else 'MISSING'}")
        if not present:
            problems.append(name)
    try:
        credentials = json.loads((PROJECT_ROOT / "credentials.json").read_text(encoding="utf-8-sig"))
        if "installed" not in credentials:
            print("Gmail: replace credentials.json with a Desktop app OAuth client download.")
            problems.append("Gmail Desktop app credentials")
        else:
            print("Gmail: Desktop app credentials present.")
    except (OSError, ValueError):
        print("Gmail: credentials.json is missing or invalid JSON.")
        problems.append("Gmail credentials")
    print(f"Gmail saved login: {'present' if (PROJECT_ROOT / 'token.json').exists() else 'first-run Google sign-in needed'}")
    if os.getenv("GROQ_API_KEY"):
        try:
            request = Request("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}", "User-Agent": "email-automation-setup/1.0"})
            with urlopen(request, timeout=30) as response:
                available = {model["id"] for model in json.load(response)["data"]}
            if GROQ_MODEL not in available:
                raise ValueError("Configured model unavailable")
            print(f"Groq: API key accepted; {GROQ_MODEL} available.")
        except (HTTPError, URLError, ValueError) as error:
            print(f"Groq: check failed ({type(error).__name__}, HTTP {getattr(error, 'code', 'n/a')}).")
            problems.append("Groq API access")
    if os.getenv("GOOGLE_API_KEY"):
        try:
            request = Request(
                f"https://generativelanguage.googleapis.com/v1beta/{EMBEDDING_MODEL}:embedContent",
                data=json.dumps({"model": EMBEDDING_MODEL, "content": {"parts": [{"text": "Setup connection test"}]}}).encode(),
                headers={"x-goog-api-key": os.environ["GOOGLE_API_KEY"], "Content-Type": "application/json"},
            )
            with urlopen(request, timeout=30) as response:
                dimensions = len(json.load(response)["embedding"]["values"])
            print(f"Google: embedding request passed ({dimensions} dimensions).")
        except (HTTPError, URLError, ValueError) as error:
            print(f"Google: embedding request failed ({type(error).__name__}, HTTP {getattr(error, 'code', 'n/a')}).")
            problems.append("Google embedding API access")
    print(f"Knowledge index: {'present' if (Path(VECTORSTORE_DIR) / 'chroma.sqlite3').exists() else 'run .\\run.ps1 index'}")
    if problems:
        print("Action needed: " + ", ".join(problems))
        return 1
    print("Configuration checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
