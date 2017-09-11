#!/usr/bin/env python3

"""
Wrapper for tpen2tei.json2xml
"""

import argparse
import importlib
import os
import sys
import tpen2tei.json2xml


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
    parser.add_argument (
        "-c",
        "--config",
        help = "a Python module with any necessary custom definitions",
    )

    args = parser.parse_args()

    #  logging.basicConfig (
    #      format = '%(asctime)s %(message)s',
    #      filename = '%s.log' % os.path.basename (sys.argv[0]),
    #  )
    configmod = None
    if args.config is not None:
        configpath = os.path.expanduser(args.config)
        sys.path.append(os.path.dirname(configpath))
        configmod = os.path.basename(configpath)

    tpen2tei.json2xml.json2xml (
        indir               = args.indir,
        outdir              = args.outdir,
        write_stdout_stderr = args.write_stdout_stderr,
        metadata            = metadata(configmod),            # wants a dict or None
        special_chars       = special_chars(configmod),       # wants a dict or None
        numeric_parser      = numeric_parser(configmod),      # wants a function or None
        text_filter         = transcription_filter(configmod) # wants a function or None
    )
