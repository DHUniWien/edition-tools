#!/usr/bin/env python3

import yaml
import tempfile
import os
import re
import logging
import datetime
import json

from tpen import TPen
from command import run


repo_prefix = 'ssh://git@github.com/DHUniWien/'
repo_name   = 'MatthewEdessa'
repo        = repo_prefix + repo_name

def get_config():
    with open ('./backup.yml', 'r') as ymlfile:
        return yaml.load (ymlfile)


def setup (config):
    tpen = TPen (cfg = config)

    logging.basicConfig (
        format = '%(asctime)s %(message)s',
        filename = config.get ('logfile'),
        level = config.get ('loglevel'),
    )

    return tpen

def backup (**kwa):
    tpen = kwa.get ('tpen')
    config = kwa.get ('config')

    with tempfile.TemporaryDirectory() as tmpdir:
        logging.info("temp directory is %s" % tmpdir)
        os.chdir (tmpdir)
        run (['/usr/bin/git', 'clone',  repo])
        os.chdir (repo_name + '/transcription/')
        project_members = dict()
        new_members = set()

        # delete obsolete files
        #
        for f in os.listdir():
            if f in config.get ('keeplist'):
                logging.error ('keeping file <%s>' % f)
                
            # scan existing project members
            elif f == 'members.json':
                with open(f, encoding='utf-8') as fh:
                    project_members = json.load(fh)

            # delete what is not on T-PEN anymore
            elif f not in ['%s.json' % p.get ('label') for p in tpen.projects_list()]:
                logging.error ('file <%s> is obsolete and will be deleted' % f)
                run (['/usr/bin/git', 'rm', f])

            # delete what is blacklisted
            elif f in ['%s.json' % b for b in config.get ('blacklist')]:
                logging.error ('file <%s> blacklisted and will be deleted' % f)
                run (['/usr/bin/git', 'rm', f])


        for project in tpen.projects():

            # implement a simple blacklist
            #
            if project.get ('label') in config.get ('blacklist'):
                logging.info (
                    'project <%s> is blacklisted' %
                    project.get ('tpen_id')
                )

            elif project.get ('data'):
                content = project.get('data')
                with open ('./%s.json' % (project.get ('label')), 'w') as fh:
                    # Scan the data for new user IDs
                    for m in re.finditer(r'\"_tpen_creator\"\s+:\s+(\d+)', content):
                        if m.group(1) not in project_members:
                            new_members.add(m.group(1))
                    fh.write (content)

            # option write-garbage
            else:
                logging.info ('no data for project <%s>' % project.get ('tpen_id'))
                with open ('./%s.json.garbage' % (project.get ('label')), 'w') as fh:
                    fh.write (project.get ('garbage'))
                    
        # look up and add any new users we found
        found_new_member = False
        for uid in new_members:
            newuser = tpen.user(uid = uid)
            logging.debug('retrieved new user %s' % newuser)
            if newuser is not None:
                found_new_member = True
                project_members[uid] = newuser
                
        # write the userlist to a file
        if found_new_member:
            with open ('./members.json', 'w', encoding='utf-8') as fh:
                json.dump(project_members, fh, ensure_ascii=False, indent=2)

        # add all  *.json files for later  inspection just in case,  but not the
        # .garbage files, never  the *.garbage files; they are  for looking, not
        # for touching
        run (['/usr/bin/git', 'add', '*json'])

        logging.info (
            '`git status` says: %s' %
            run (['/usr/bin/git', 'status']).get ('stdout')
        )

        # option backup data
        run (['/bin/cp', '-r', tmpdir,
            '/tmp/tpen-backup-%s' % datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        ])

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
    config = get_config()
    os.environ.update (dict (GIT_SSH_COMMAND = "ssh -i %s" % config.get ('identity_file')))

    tpen = setup (config)
    backup (tpen = tpen, config = config)
    log_global_errors (ge = tpen.global_errors())
