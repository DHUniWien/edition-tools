#!/usr/bin/env python3

"""
merge the given T-PEN projects into one json file each
"""


import argparse
import fnmatch
import re
import os
import json
import itertools


def manuscripts(indir):
    """Figure out from the list of filenames in 'indir' which MSS we have and what 
       their short IDs should be."""
    allfound = []
    jsonfiles = sorted([x for x in os.listdir(indir) if x.endswith('.json')])
    lastms = ""
    currdict = None
    for f in jsonfiles:
        thisms = f.replace('.json', '')
        m = re.match(r'^(.*)\s+\d+\.json$', f) # it is multi-part
        if m is not None:
            thisms = m.group(1)
        if thisms != lastms:
            # Close out the last dictionary
            if currdict is not None:
                allfound.append(currdict)
            # Start the new dictionary
            lastms = thisms
            id = re.match(r'^([^(]+\w)(\s+\()?', thisms)
            currdict = {'name': id.group(1), 'files': [f]}
        else:
            currdict.get('files').append(f)
    allfound.append(currdict)
    return allfound


def main (args):
    msset = [(m['name'], m['files']) for m in manuscripts(args.indir)]
    if args.msid is not None:
        msset = [m for m in msset if m[0] in args.msid]
    for (name, files) in msset:
        if args.verbose:
            print ("merging {}".format (name))

        files = list (files)

        head_file = list (files).pop(0)
        metadata = json.load (open ('%s/%s' % (args.indir, head_file))).get ('metadata')

        # becomes a list of ( list of objects/canvases)
        canvases = [
            json.load (open ('%s/%s' % (args.indir, part))).get ('sequences')[0].get ('canvases')
            for part in files
        ]

        out = dict (
            metadata = metadata,
            sequences = [ dict (
                # flatten out canvases
                canvases = [c for perfile in canvases for c in perfile]
            ) ],
        )

        json.dump (out, open ('%s/%s-merged.json' % (args.outdir, name), 'w'), sort_keys = True, indent = 4)


if __name__ == "__main__":
    #  logging.basicConfig (
    #      format = '%(asctime)s %(message)s',
    #      filename = '%s.log' % os.path.basename (sys.argv[0]),
    #  )

    parser = argparse.ArgumentParser()
    parser.add_argument (
         "indir",
         help = "input directory t-pen output files",
    )
    parser.add_argument (
        "outdir",
        help = "output directory",
    )
    parser.add_argument (
        "-m",
        "--msid",
        action = "append",
        help = "specify one or more specific manuscript IDs to parse",
    )
    parser.add_argument (
        "-w",
        "--write_stdout_stderr",
        action = "store_true",
        help = "write stdout and stderr to separate files in outdir",
    )
    parser.add_argument (
        "-v",
        "--verbose",
        action = "store_true",
        help = "make output more verbose",
    )

    args = parser.parse_args()

    main (args)
