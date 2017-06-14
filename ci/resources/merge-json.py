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


def main (args):
    # n ... name
    # c ... code
    # s ... sequence
    #
    # "M5587 (J) 1"
    #  n      c  s
    #
    prog = re.compile ('(?P<name>[a-zA-z0-9]*)(?: \((?P<code>\w)\))?(?: (?P<sequence>\d))?')

    res = itertools.groupby (
        sorted (fnmatch.filter (os.listdir (args.indir), '*json')),
        lambda key: prog.match (key).group ('name')
    )

    for key, group in res:
        group = list (group)

        head_file = list (group).pop()
        metadata = json.load (open ('%s/%s' % (args.indir, head_file))).get ('metadata')

        # becomes a list of ( list of objects/canvases)
        canvases = [
            json.load (open ('%s/%s' % (args.indir, part))).get ('sequences')[0].get ('canvases')
            for part in group
        ]

        out = dict (
            metadata = metadata,
            sequences = dict (
                # flatten out canvases
                canvases = [c for perfile in canvases for c in perfile]
            ),
        )

        json.dump (out, open ('%s/%s-merged.json' % (args.outdir, key), 'w'), sort_keys = True, indent = 4)


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
        "-w",
        "--write_stdout_stderr",
        action = "store_true",
        help = "write stdout and stderr to separate files in outdir",
    )

    args = parser.parse_args()

    main (args)
