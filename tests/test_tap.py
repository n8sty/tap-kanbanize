import json
import sys
import unittest
from io import StringIO

from tap_kanbanize import discover


class test_discovery(unittest.TestCase):

    def test_returns_json(self):
        captured_stdout = StringIO()
        sys.stdout = captured_stdout
        discover()  # should be captured by the redirect above
        self.assertIsInstance(captured_stdout.getvalue(), str)
        self.assertIsInstance(json.loads(captured_stdout.getvalue()), dict)
