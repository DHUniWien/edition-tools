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


def postprocess(configmod):
    """Return a function that modifies the finished TEI product"""
    if configmod is not None:
        config = importlib.import_module(configmod)
        pp = getattr(config, "postprocess", None)
        return pp
    return None


def json2xml(indir, outdir,
             metadata=None,
             special_chars=None,
             numeric_parser=None,
             text_filter=None,
             postprocess=None):
    """ json2xml assumes all files in indir to be T-PEN output
        and tries to convert them to TEI-XML in outdir"""

    # Find the members file, if it exists in indir
    transcriptions = []
    members=None
    for infile in fnmatch.filter(os.listdir(indir), '*json'):
        if infile == 'members.json':
            with open(os.path.join(indir, infile), encoding="utf-8") as mj:
                members = json.load(mj)
        else:
            transcriptions.append(infile)

    # Now go through the transcription files
    for infile in transcriptions:
        outfile = infile + '.tei.xml'
        
        with open(indir + '/' + infile, 'r') as fh:
            data = json.load(fh)

            try:
                logging.info('starting on file <%s>' % infile)

                tei = from_sc(
                    data,
                    # from_sc will modify the supplied param metadata
                    # which would stick without deepcopy'ing every turn
                    metadata=copy.deepcopy(metadata),
                    members=members,
                    special_chars=special_chars,
                    numeric_parser=numeric_parser,
                    text_filter=text_filter,
                    postprocess=postprocess
                )

                # just ignore tei==None
                if tei:
                    tei.write(
                        outdir + '/' + outfile,
                        encoding='utf8',
                        pretty_print=True,
                        xml_declaration=True
                    )

                    logging.info('file <%s> looks good' % infile)
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
        "-v",
        "--verbose",
        action="store_true",
        help="turn on more verbose logging",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="a Python module with any necessary custom definitions",
    )

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    configmod = None
    if args.config is not None:
        configpath = os.path.expanduser(args.config)
        sys.path.append(os.path.dirname(configpath))
        configmod = os.path.basename(configpath)

    json2xml(args.indir, args.outdir,
             metadata=metadata(configmod),                 # wants a dict or None
             special_chars=special_chars(configmod),       # wants a dict or None
             numeric_parser=numeric_parser(configmod),     # wants a function or None
             text_filter=transcription_filter(configmod),  # wants a function or None
             postprocess=postprocess(configmod)            # wants a function or None
             )
