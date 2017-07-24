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


def manuscripts ():
    return [
        { 'name' : 'Bz449',
          'files' : ['Bz449 (K) .json'],
        },
        { 'name' : 'Bzommar, Armenian Catholic Clergy Institute 430',
          'files' : ['Bzommar, Armenian Catholic Clergy Institute 430.json'],
        },
        { 'name' : 'M1731',
          'files' : [
            'M1731 (F) 1.json',
            'M1731 (F) 2.json',
            'M1731 (F) 3.json',
          ]
        },
        { 'name' : 'M1767',
          'files' : [
            'M1767 (B) 1.json',
            'M1767 (B) 2.json',
            'M1767 (B) 3.json',
            'M1767 (B) 4.json',
            'M1767 (B) 5.json',
            'M1767 (B) 6.json',
            'M1767 (B) 7.json',
          ]
        },
        { 'name' : 'M1768',
          'files' : [
            'M1768 (H) 1.json',
            'M1768 (H) 2.json',
            'M1768 (H) 3.json',
          ]
        },
        { 'name' : 'M1768',
          'files' : [
            'M1769 (I) 1.json',
            'M1769 (I) 2.json',
            'M1769 (I) 3.json',
          ]
        },
        { 'name' : 'M1896',
          'files' : [
            'M1896 (A) 1.json',
            'M1896 (A) 2.json',
            'M1896 (A) 3.json',
            'M1896 (A) 4.json',
          ]
        },
        { 'name' : 'M2644',
          'files' : [
            'M2644 (G) 1.json',
            'M2644 (G) 2.json',
          ]
        },

        { 'name' : 'M3017',
          'files' : [
            'M3071 (C).json',
          ]
        },

        { 'name' : 'M3519',
          'files' : [
            'M3519 (D).json',
          ]
        },

        { 'name' : 'M3520',
          'files' : [
            'M3520 (E) 1.json',
            'M3520 (E) 2.json',
            'M3520 (E) 3.json',
            'M3520 (E) 4.json',
          ]
        },

        { 'name' : 'M5587',
          'files' : [
            'M5587 (J) 0.json',
            'M5587 (J) 1.json',
            'M5587 (J) 2.json',
            'M5587 (J) 3.json',
            'M5587 (J) 4.json',
          ]
        },
        { 'name' : 'OXE32',
          'files' : [
            'Ox e.32 (O) 0.json',
            'Ox e.32 (O) 1.json',
            'Ox e.32 (O) 2.json',
            'Ox e.32 (O) 3.json',
          ]
        },
        { 'name' : 'V887',
          'files' : [
            'V887 (V) 1.json',
            'V887 (V) 2.json',
            'V887 (V) 3.json',
          ]
        },
        { 'name' : 'V901',
          'files' : [
            'V901 (X) 1.json',
            'V901 (X) 2.json',
          ]
        },
        { 'name' : 'V913',
          'files' : [
            'V913 (Y).json',
          ]
        },
        { 'name' : 'V917',
          'files' : [
            'V917 (Z) 0.json',
            'V917 (Z) 1.json',
            'V917 (Z) 2.json',
          ]
        },
        { 'name' : 'W243',
          'files' : [
            'W243 1.json',
            'W243 2.json',
          ]
        },
        { 'name' : 'W246',
          'files' : [
            'W246.json',
          ]
        },
        { 'name' : 'W574',
          'files' : [
            'W574 (W) 1.json',
            'W574 (W) 2.json',
          ]
        },
    ]


def main (args):
    for (name, files) in [(m['name'], m['files']) for m in manuscripts()]:
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
