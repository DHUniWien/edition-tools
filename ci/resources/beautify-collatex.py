import os
import fnmatch
import argparse
import json


def run (args):
    for infile in fnmatch.filter (os.listdir (args.indir), '*json'):
        json_in = json.load (open ('%s/%s' % (args.indir, infile), 'r'))
        outfile = '%s/%s' % (args.outdir, infile)

        with open (outfile, 'w') as fh_out:
            json.dump (
                json_in,
                fh_out,
                ensure_ascii = False,
                indent = 4,
                check_circular = True,
            )


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument (
         "indir",
         help = "input directory",
    )
    parser.add_argument (
        "outdir",
        help = "output directory",
    )

    args = parser.parse_args()
    run (args)
