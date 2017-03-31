import unittest
from command import run

class TestCommand (unittest.TestCase):

    def test_command (self):
        self.assertEqual (
            run (['ls', './command.py']),
            {'returncode': 0, 'stdout': b'./command.py\n', 'stderr': b''},
        )

        self.assertEqual (
            run (['ls', './COMMAND.PY']),
            {'returncode': 2, 'stdout': b'', 'stderr': b"ls: cannot access './COMMAND.PY': No such file or directory\n"},
        )
