import logging
import os
import fnmatch
import sys
import pprint
import argparse
import json
import re
import importlib

from tpen2tei.wordtokenize import from_string


def milestones(configmod):
    """Returns a list of milestones that should be individually collated"""
    if configmod is not None:
        mst = getattr(configmod, "milestones", None)
        if mst is not None:
            return mst()
    return []


def normalise(configmod):
    """Returns a function that takes a token and modifies it, or None"""
    if configmod is not None:
        na = getattr(configmod, "normalise", None)
        return na
    return None
    


def teixml2collatex(milestone, indir, verbose, configmod):
    # list elements are already so
    # that collatex can digest them
    collation = dict (witnesses = list())

    # walk through all available witnesses
    # and look for the current milestone
    #
    # presume: one witness per file
    for infile in fnmatch.filter (os.listdir (indir), '*tei.xml'):
        if verbose:
            print ("milestone {} in file: {}".format (milestone, infile))

        # remove file ext. and a possible substring '-merged' (exists
        # for witnesses that were merged from multiple files into one
        witness_name = re.sub ('-merged', '', infile[:infile.find('.')])

        tokens = extract_tokens (
            xmlfile   = indir + '/' + infile,
            milestone = milestone,
            configmod = configmod
        )

        if tokens:
            collation.get ('witnesses').append (dict (
                id     = witness_name,
                tokens = tokens,
            ))
            logging.info ('milestone <%s> found in witness file <%s>' % (
                milestone,
                infile,
            ))
        else:
            logging.info ('milestone <%s> not found in witness file <%s>' % (
                milestone,
                infile,
            ))

    return collation


def extract_tokens (**kwa):
    """ returns json
    """

    xmlfile   = kwa.get ('xmlfile')
    milestone = kwa.get ('milestone')
    configmod = kwa.get ('configmod')

    try:
        with open (xmlfile, encoding = 'utf-8') as fh:
            return from_string (
                fh.read(),
                milestone    = milestone,
                first_layer  = False,
                normalisation = normalise(configmod)
            )
    except FileNotFoundError:
        logging.info ('file not found: %s' % xmlfile)
    except:
        logging.info ('exception type: %s' % sys.exc_info()[0])
        logging.info ('exception value: %s' % sys.exc_info()[1])
        logging.info ('exception trace: %s' % sys.exc_info()[2])


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
        "-v",
        "--verbose",
        action = "store_true",
        help = "make output more verbose",
    )
    parser.add_argument (
        "-c",
        "--config",
        help = "module for custom collation logic"
    )

    logging.basicConfig (
        format = '%(asctime)s %(message)s',
        filename = '%s.log' % os.path.basename (sys.argv[0]),
        level = logging.NOTSET,
    )

    args = parser.parse_args()
    
    configmod = None
    if args.config is not None:
        configpath = os.path.expanduser(args.config)
        sys.path.append(os.path.dirname(configpath))
        configmod = importlib.import_module(os.path.basename(configpath))
    
    for milestone in milestones(configmod):
        c = teixml2collatex(milestone, args.indir, args.verbose, configmod)
        if c.get ('witnesses'):
            outfile = '%s/milestone-%s.json' % (args.outdir, milestone)

            with open (outfile, 'w') as fh:
                json.dump (
                    c,
                    fh,
                    ensure_ascii = False,
                    indent = 4,
                    check_circular = True,
                )
