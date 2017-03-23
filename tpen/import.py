#!/usr/bin/env python3

import os
import re
import tempfile
import logging

from command import run

indir       = '/home/oftl/univie/t-pen.org/tpen-backup/'
repo_prefix = 'ssh://git@github.com/oftl/'
repo_name   = 'MatthewEdessa'
repo        = repo_prefix + repo_name
p           = re.compile ('^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})$')

with tempfile.TemporaryDirectory() as tmpdir:
    os.chdir (tmpdir)
    run (['/usr/bin/git', 'clone',  repo])

    for d in sorted (os.listdir (indir)):
        m = re.match (p, d)

        # ISA backup!
        if m:
            outdir = tmpdir + '/' + repo_name + '/transcription/'
            logging.info ('d %s' % d.rjust (10))
            logging.info ('outdir %s' % outdir.rjust(10))


            for z in os.listdir (indir + '/' + d):
                zipfile = indir + '/' + d +'/' + z

                logging.info ('zipfile %s' % zipfile.rjust (10))

                run (['/usr/bin/unzip', '-o', zipfile, '-d', outdir])

            logging.info ('all unziperrero')
            os.chdir (outdir)

            run (['/usr/bin/git', 'add', '*json'])
            run ([
                '/usr/bin/git', 'commit',
                '-m', 'T-PEN backup automagick; Originally pulled from T-PEN on %s-%s-%s' % (
                    m.group ('year'),
                    m.group ('month'),
                    m.group ('day'),
            )])

            run (['/usr/bin/git', 'push'])
