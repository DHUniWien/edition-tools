#!/usr/bin/env python3

import yaml
import tempfile
import os
import re
import logging

from tpen import TPen
from command import run


repo_prefix = 'ssh://git@github.com/oftl/'
repo_name   = 'MatthewEdessa'
repo        = repo_prefix + repo_name


def setup():
    with open ('./backup.yml', 'r') as ymlfile:
        cfg = yaml.load (ymlfile)
        tpen = TPen (cfg = cfg)

        logging.basicConfig (
            format = '%(asctime)s %(message)s',
            filename = cfg.get ('logfile'),
            level = cfg.get ('debug') and logging.DEBUG or logging.ERROR,
        )

        return tpen

def backup (**kwa):
    tpen = kwa.get ('tpen')

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir (tmpdir)
        run (['/usr/bin/git', 'clone',  repo])
        os.chdir (repo_name + '/transcription/')

        for project in tpen.projects():
            with open ('./%s.json' % (project.get ('label')), 'w') as fh:
                fh.write (project.get ('data'))

        run (['/usr/bin/git', 'add', '*json'])

        logging.info (
            '`git status` says: %s' %
            run (['/usr/bin/git', 'status']).get ('stdout')
        )

        ret = run (['/usr/bin/git', 'commit', '-m', 'T-PEN backup automagick'])

        m = re.match (
            ".*Your branch is up-to-date with 'origin/master'.*",
            str (ret.get ('stdout')),
        )

        if m:
            logging.info ('no newer versions found on t-pen.org')
        else:
            logging.info ('pushing updates to github')
            run (['/usr/bin/git', 'push'])


if __name__ == '__main__':
    backup (tpen = setup())
