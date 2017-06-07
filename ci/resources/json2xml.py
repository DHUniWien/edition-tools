#!/usr/bin/env python3

"""
Wrapper for tpen2tei.json2xml
"""

import argparse

import tpen2tei.json2xml


def metadata():
    return None

def special_chars():
    return None

def numeric_parser():
    return None

if __name__ == '__main__':

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

    #  logging.basicConfig (
    #      format = '%(asctime)s %(message)s',
    #      filename = '%s.log' % os.path.basename (sys.argv[0]),
    #  )

    json2xml.json2xml (
        indir               = args.indir,
        outdir              = args.outdir,
        write_stdout_stderr = args.write_stdout_stderr,
        metadata            = metadata(),
        special_chars       = special_chars(),
        numeric_parser      = numeric_parser(),
    )
