import requests
import requests_mock
import unittest
import yaml
import re

from tpen import TPen

CONFIG_FILE = './backup.yml'
INDEX_FILE = './tests/files/index.htm'
PROJECT_FILE = './tests/files/project-35.ld+json'

class TestHTTP (unittest.TestCase):

    def setUp (self):
        with open (CONFIG_FILE, 'r') as ymlfile:
            self.cfg = yaml.load (ymlfile, Loader=yaml.FullLoader)

    def test_login_ok (self):
        login_success = 'document.location = "index.jsp";'

        with requests_mock.Mocker() as m:
            m.post (self.cfg.get ('uri_login'), text = login_success)
            tpen = TPen (cfg = self.cfg)

    def test_login_nok (self):
        login_success = 'document.location = "doh!";'

        with requests_mock.Mocker() as m:
            m.post (self.cfg.get ('uri_login'), text = login_success)

            self.assertRaises (
                UserWarning,
                TPen,
                cfg = self.cfg,
            )

    def test_projects_list (self):
        login_success = 'document.location = "index.jsp";'

        with requests_mock.Mocker() as m:
            m.post (self.cfg.get ('uri_login'), text = login_success)
            tpen = TPen (cfg = self.cfg)

            with open (INDEX_FILE, 'r') as fh:
                m.get (
                    self.cfg.get ('uri_index'),
                    text = fh.read(),
                )

            self.assertEqual (len (tpen.projects_list()), 13)

            match = re.compile ('^%s\d+$' % self.cfg.get ('uri_project'))

            with open (PROJECT_FILE, 'r') as fh:
                m.get (match, text = fh.read())

            self.assertEqual (len (tpen.projects_as_list()), 13)
            self.assertEqual (sum (1 for two in tpen.projects()), 13)
