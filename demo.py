"""Exercise the real AI workflow with sample data and no Gmail access."""
from unittest.mock import patch
from src.graph import Workflow
from src.config import PROJECT_ROOT, EMBEDDING_MODEL
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

SAMPLE_EMAIL = {
    "id": "demo-1", "threadId": "demo-thread", "messageId": "<demo@example.com>",
    "references": "", "sender": "customer@example.com", "subject": "Pricing question",
    "body": "Hello, what are the pricing options for your AI agency platform? Thank you, Sam.",
}


class DemoGmail:
    def __init__(self):
        self.drafts = []

    def fetch_unanswered_emails(self):
        return [SAMPLE_EMAIL.copy()]

    def create_draft_reply(self, email, text):
        self.drafts.append(text)
        print("\nDEMO DRAFT (not saved or sent to Gmail):\n" + text)
        return {"id": "demo-draft"}


def main():
    demo_dir = str(PROJECT_ROOT / "db_demo")
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    store = Chroma(persist_directory=demo_dir, embedding_function=embeddings)
    if store._collection.count() == 0:
        print("Building an index from synthetic sample text only...")
        store.add_texts([
            "This is a fictional demo business. Its Starter plan costs $19 per month and includes 100 tasks. "
            "Its Pro plan costs $49 per month and includes 1,000 tasks. Both plans include email support. "
            "These are sample prices only, not real business offers."
        ], ids=["synthetic-pricing-v1"])
    gmail = DemoGmail()
    with patch("src.nodes.GmailToolsClass", return_value=gmail), patch("src.agents.VECTORSTORE_DIR", demo_dir):
        workflow = Workflow().app
        result = workflow.invoke({
            "emails": [], "current_email": SAMPLE_EMAIL,
            "email_category": "", "generated_email": "", "rag_queries": [],
            "retrieved_documents": "", "writer_messages": [],
            "sendable": False, "trials": 0,
        }, {"recursion_limit": 100})
    assert not result["emails"], "Sample email was not processed"
    assert gmail.drafts, "The proofreader did not approve a sample draft"
    print("\nDemo completed. No Gmail messages were read, created, or sent.")


if __name__ == "__main__":
    main()
