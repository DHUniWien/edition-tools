import requests
import re
import hashlib
import logging
from bs4 import BeautifulSoup


class TPen (object):
    """ TPen acts as an abstraction layer from t-pen.org
    """

    def __init__ (self, **kwa):
        """ the following keys are possible in the mandatory cfg dict

            username
            password ............. t-pen credentials
            debug ................ additional debug logging
            logfile .............. logfile location
            timeout .............. timeout when accessing t-pen
            timeout_errors_max ... give up after this many timeouts

            init will try to login into t-pen or fail miserably
        """

        cfg = kwa.get ('cfg')

        self.timeout = cfg.get ('timeout')
        self.timeout_errors_max = cfg.get ('timeout_errors_max')
        self.timeout_errors = 0
        self.cookies = None

        self.uri_index = 'http://t-pen.org/TPEN/index.jsp'
        self.uri_login = 'http://t-pen.org/TPEN/login.jsp'
        self.uri_project = 'http://t-pen.org/TPEN/project/'

        logging.basicConfig (
            format = '%(asctime)s %(message)s',
            filename = cfg.get ('logfile'),
            level = cfg.get ('debug') and logging.DEBUG or logging.ERROR,
        )

        # login in
        #
        md5_login_failed = 'b9abb18f4c42fd8321f97d38790d224d'
        login_success = 'document.location = "index.jsp";'

        res = self._request (
            verb = 'post',
            uri = self.uri_login,
            data = dict (
                uname    = cfg.get ('username'),
                password = cfg.get ('password'),
        ))

        d = hashlib.md5 ()
        d.update (res.text.encode())

        # res.cookies is always set regardles off login success or error

        logged_in = False
        while not logged_in and self.timeout_errors <= self.timeout_errors_max:
            self.timeout_errors += 1

            # "well" known md5 of response returned by t-pen in case of error
            if (md5_login_failed == d.hexdigest()):
                logging.error ('[001] authentication failed (try %s)' % self.timeout_errors)

            # "well" known response returned by t-pen in case of success
            elif login_success not in res.text:
                logging.error ('[002] authentication failed (try %s)' % self.timeout_errors)
                logging.debug ('[002] res.headers %s: ' % res.headers)
                logging.debug ('[002] res.history %s: ' % res.history)
                logging.debug ('[002] res.text %s: ' % res.text)

            else:
                logged_in = True

        if not logged_in:
            raise UserWarning ('[002] authentication failed')
        else:
            logging.info ('today it took %s tries to login' % self.timeout_errors)

        self.timeout_errors = 0
        self.cookies = res.cookies


    def projects_list (self):
        """ get a list of all projects of logged in account
            the list consists of dicts with the two keys label and project_id
        """

        projects = []

        soup = BeautifulSoup (self._request (uri = self.uri_index).text, 'html.parser')
        table = soup.find (id = 'projectList')

        # link target may not change
        # projectID is supposed to be the first parameter
        #
        p = re.compile ('^transcription.html\?projectID=(\d+).*')

        for tr in table.tbody.find_all ('tr'):
            label = tr.get ('title')
            href  = tr.td.a.get ('href')
            match = p.match (href)

            label and match and projects.append (dict (
                label = tr.get ('title'),
                project_id = match.group (1),
            ))

        return projects


    def project (self, **kwa):
        """ get a single project
            the given project dict will be updated with a corrensponding data key and returned
        """

        project = kwa.get ('project')
        res  = self._request (self.uri_project + project.get ('project_id'))

        if res.ok and res.text:
            logging.debug ('got project "%s" ("%s")' % (
                project.get ('label'),
                project.get ('project_id'),
            ))

            project.update (data = res.text)
            return project
        else:
            logging.warning ('could not download project "%s" from: "%s"' % (
                project.get ('project_id'),
                uri,
            ))


    def projects (self, **kwa):
        """ get all projects of logged in account
        """

        for project in self.projects_list():
            yield self.project (project = project)


    def _request (self, uri, **kwa):
        """ issues a request to the given uri and return the response as is
            defaults to GET
        """

        uri  = uri or kwa.get ('uri')
        verb = kwa.get ('verb') or 'get'
        data = kwa.get ('data')

        try:
            if verb == 'post':
                res = requests.post (
                    uri,
                    data = data,
                    cookies = self.cookies,
                    timeout = self.timeout,
                )
            elif verb == 'get':
                res = requests.get (
                    uri,
                    cookies = self.cookies,
                    timeout = self.timeout,
                )
            else:
                raise UserWarning ('[004] invalid verb')

        except requests.exceptions.Timeout as e:
            logging.exception ('[003] cought requests.exceptions.Timeout')
            self.timeout_error += 1
            if self.timeout_errors >= self.timeout_errors_max:
                raise e

        return res


if __name__ == '__main__':
    pass
