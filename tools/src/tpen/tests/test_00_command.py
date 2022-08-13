import unittest
from command import run

class TestCommand (unittest.TestCase):

    def test_command (self):
        self.assertEqual (
            run (['ls', './command.py']).get ('returncode'),
            0,
        )
