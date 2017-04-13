#!/usr/bin/env python3

import yaml
import tempfile
import os
import re
import logging
import datetime

from tpen import TPen
from command import run


repo_prefix = 'ssh://git@github.com/DHUniWien/'
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
            if project.get ('data'):
                with open ('./%s.json' % (project.get ('label')), 'w') as fh:
                    fh.write (project.get ('data'))

            # option write-garbage
            else:
                logging.info ('no data for project <%s>' % project.get ('project_id'))
                with open ('./%s.json.garbage' % (project.get ('label')), 'w') as fh:
                    fh.write (project.get ('garbage'))

        # option backup data
        run (['/bin/cp', '-r', tmpdir,
            '/tmp/tpen-backup-%s' % datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        ])

        # add all  *.json files for later  inspection just in case,  but not the
        # .garbage files, never  the *.garbage files; they are  for looking, not
        # for touching
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


def log_global_errors (**kwa):
    ge = kwa.get ('ge')

    # XXX there might be room for improvement here
    #
    k_width = max ([ len(k) + 2 for k in ge.keys() ])
    v_width = max ([ len(str(v)) for v in ge.values() ])

    [ logging.info (
        '[error report] %s %s' % (
            error.ljust (k_width),
            str (count).rjust (v_width),
      ))
      for (error, count) in sorted (ge.items(), key = lambda kv: kv[0])
    ]


if __name__ == '__main__':
    tpen = setup()
    backup (tpen = tpen)
    log_global_errors (ge = tpen.global_errors())
