#!/usr/bin/env python3

import yaml
import os
import re
import sys
import logging
import json

from tpen import TPen
from command import run


def get_config():
    ourpath = os.path.abspath(os.path.dirname(__file__))
    with open ('%s/backup.yml' % ourpath, 'r') as ymlfile:
        return yaml.load(ymlfile, Loader=yaml.FullLoader)


def setup (config):
    # Set up the logging here
    logargs = {
        'format': '%(asctime)s %(message)s',
        'level': config.get('loglevel', 'INFO')
    }
    if 'logfile' in config:
        logargs['filename'] = config.get('logfile')
    else:
        logargs['stream'] = sys.stdout
    logging.basicConfig (**logargs)

    # Initialize the TPen object
    tpen = TPen (cfg = config)
    return tpen

def backup (**kwa):
    tpen = kwa.get ('tpen')
    config = kwa.get ('config')
    basedir = kwa.get ('basedir')

    os.chdir (basedir + '/transcription/')
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
    tpen = setup (config)
    backup (tpen = tpen, config = config, basedir = sys.argv[1])
    log_global_errors (ge = tpen.global_errors())
