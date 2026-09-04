"""Run one Gmail batch using the selected knowledge source, creating drafts only."""
import json
from datetime import datetime, timezone
from src.config import PROJECT_ROOT, KNOWLEDGE_MODE
from src.graph import Workflow


def main():
    app = Workflow().app
    initial_state = {
        "emails": [], "email_category": "", "generated_email": "",
        "rag_queries": [], "retrieved_documents": "", "writer_messages": [],
        "sendable": False, "trials": 0,
    }
    summary = {"knowledge_mode": KNOWLEDGE_MODE, "loaded": 0, "categorized": 0,
               "drafts_created": 0, "unrelated_skipped": 0, "review_failed": 0}
    print(f"Starting one live Gmail batch with {KNOWLEDGE_MODE} knowledge. Drafts only.", flush=True)
    for output in app.stream(initial_state, {"recursion_limit": 1000}):
        for key, value in output.items():
            if key == "load_inbox_emails":
                summary["loaded"] = len(value["emails"])
                print(f"Eligible emails: {summary['loaded']}", flush=True)
            counter = {"categorize_email": "categorized", "send_email": "drafts_created",
                       "skip_unrelated_email": "unrelated_skipped", "discard_failed_email": "review_failed"}.get(key)
            if counter:
                summary[counter] += 1
    summary["completed_at"] = datetime.now(timezone.utc).isoformat()
    (PROJECT_ROOT / "last_run.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Batch complete: " + json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
