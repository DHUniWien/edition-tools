#!/usr/bin/env python3

"""
Wrapper for tpen2tei.json2xml
"""

import argparse
import copy
import fnmatch
import importlib
import json
import logging
import os
import sys
import traceback
from tpen2tei.parse import from_sc


def metadata(configmod):
    """Return a dictionary suitable for the 'metadata' parameter to from_sc."""
    if configmod is not None:
        config = importlib.import_module(configmod)
        md = getattr(config, "metadata", None)
        return md
    return None


def special_chars(configmod):
    """Return a dict of non-Unicode glyphs that may occur in the manuscript"""
    if configmod is not None:
        config = importlib.import_module(configmod)
        sc = getattr(config, "special_chars", None)
        return sc
    return None


def numeric_parser(configmod):
    """Return a function that parses the content of <num> tags into a numeric value"""
    if configmod is not None:
        config = importlib.import_module(configmod)
        np = getattr(config, "numeric_parser", None)
        return np
    return None

    
def transcription_filter(configmod):
    """Return a function that filters a line of transcription before XMLification"""
    if configmod is not None:
        config = importlib.import_module(configmod)
        tf = getattr(config, "transcription_filter", None)
        return tf
    return None


def json2xml(indir, outdir,
             metadata=None,
             special_chars=None,
             numeric_parser=None,
             text_filter=None,
             write_stdout_stderr=False):
    """ json2xml assumes all files in indir to be T-PEN output
        and tries to convert them to TEI-XML in outdir"""

    for infile in fnmatch.filter(os.listdir(indir), '*json'):
        outfile = infile + '.tei.xml'

        if write_stdout_stderr:
            sys.stdout = open(outdir + '/' + infile + '.stdout', 'w')
            sys.stderr = open(outdir + '/' + infile + '.stderr', 'w')

        with open(indir + '/' + infile, 'r') as fh:
            data = json.load(fh)

            try:
                logging.error('starting on file <%s>' % infile)

                tei = from_sc(
                    data,
                    # from_sc will modify the supplied param metadata
                    # which would stick without deepcopy'ing every turn
                    metadata=copy.deepcopy(metadata),
                    special_chars=special_chars,
                    numeric_parser=numeric_parser,
                    text_filter=text_filter
                )

                # just ignore tei==None
                if tei:
                    tei.write(
                        outdir + '/' + outfile,
                        encoding='utf8',
                        pretty_print=True,
                        xml_declaration=True
                    )

                    logging.error('file <%s> looks good' % infile)
                else:
                    logging.error('error with file <%s>: tpen2tei.parse.from_sc did not return anything' % infile)

            except Exception:
                logging.error('error with file <%s>: %s\n' % (infile, traceback.format_exc()))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
         "indir",
         help="input directory t-pen output files",
    )
    parser.add_argument(
        "outdir",
        help="output directory",
    )
    parser.add_argument(
        "-w",
        "--write_stdout_stderr",
        action="store_true",
        help="write stdout and stderr to separate files in outdir",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="a Python module with any necessary custom definitions",
    )

    args = parser.parse_args()

    configmod = None
    if args.config is not None:
        configpath = os.path.expanduser(args.config)
        sys.path.append(os.path.dirname(configpath))
        configmod = os.path.basename(configpath)

    json2xml(args.indir, args.outdir,
             write_stdout_stderr=args.write_stdout_stderr,
             metadata=metadata(configmod),                 # wants a dict or None
             special_chars=special_chars(configmod),       # wants a dict or None
             numeric_parser=numeric_parser(configmod),     # wants a function or None
             text_filter=transcription_filter(configmod)   # wants a function or None
             )
