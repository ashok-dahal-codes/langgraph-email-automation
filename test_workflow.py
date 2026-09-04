"""Regression checks for queue progress and bounded draft retries."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from src.graph import Workflow
from src.structure_outputs import EmailCategory
from demo import SAMPLE_EMAIL


class WorkflowTests(unittest.TestCase):
    def run_workflow(self, reviews):
        agents = SimpleNamespace(
            categorize_email=Mock(), email_writer=Mock(), email_proofreader=Mock(),
        )
        agents.categorize_email.invoke.return_value = SimpleNamespace(category=EmailCategory.customer_feedback)
        agents.email_writer.invoke.return_value = SimpleNamespace(email='Thank you for your feedback.')
        agents.email_proofreader.invoke.side_effect = [SimpleNamespace(send=send, feedback='Review') for send in reviews]
        gmail = Mock()
        gmail.fetch_unanswered_emails.return_value = [dict(SAMPLE_EMAIL, id='first'), dict(SAMPLE_EMAIL, id='second')]
        with patch('src.nodes.Agents', return_value=agents), patch('src.nodes.GmailToolsClass', return_value=gmail):
            result = Workflow().app.invoke({
                'emails': [], 'writer_messages': [], 'retrieved_documents': '',
                'trials': 0, 'rag_queries': [], 'sendable': False,
            }, {'recursion_limit': 100})
        self.assertEqual(result['emails'], [])
        self.assertEqual(result['writer_messages'], [])
        self.assertEqual(result['trials'], 0)
        return agents, gmail

    def test_successful_drafts_clear_history_between_emails(self):
        agents, gmail = self.run_workflow([True, True])
        self.assertEqual(gmail.create_draft_reply.call_count, 2)
        self.assertEqual(agents.email_writer.invoke.call_count, 2)

    def test_rejected_final_email_exits_and_each_email_gets_three_trials(self):
        agents, gmail = self.run_workflow([False] * 6)
        self.assertEqual(agents.email_writer.invoke.call_count, 6)
        gmail.create_draft_reply.assert_not_called()


if __name__ == '__main__':
    unittest.main()
