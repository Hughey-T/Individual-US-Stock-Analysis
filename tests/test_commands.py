import unittest

from stock_analysis_runtime.commands import Command, parse_command


class CommandTests(unittest.TestCase):
    def test_exact_next_advances(self):
        self.assertEqual(parse_command("次", initial_complete=False), Command.NEXT)

    def test_whitespace_next_does_not_advance(self):
        self.assertEqual(parse_command(" 次", initial_complete=False), Command.NONE)

    def test_embedded_next_does_not_advance(self):
        self.assertEqual(parse_command("次をお願いします", initial_complete=False), Command.NONE)

    def test_question_does_not_advance(self):
        self.assertEqual(parse_command("Phase 2とは？", initial_complete=False), Command.NONE)

    def test_update_requires_initial_completion(self):
        self.assertEqual(parse_command("更新", initial_complete=False), Command.NONE)

    def test_exact_update_after_completion(self):
        self.assertEqual(parse_command("更新", initial_complete=True), Command.UPDATE)

    def test_embedded_update_does_not_advance(self):
        self.assertEqual(parse_command("更新してください", initial_complete=True), Command.NONE)
