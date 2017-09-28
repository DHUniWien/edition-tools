import logging
import os
import fnmatch
import sys
import pprint
import argparse
import json
import re
import importlib
import statistics
import datetime

from tpen2tei.wordtokenize import Tokenizer


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
    witnesses = []

    # walk through all available witnesses
    # and look for the current milestone
    #
    # presume: one witness per file
    mslength = []
    missing = []
    tokenizer_main = Tokenizer(
        milestone=milestone,
        normalisation=normalise(configmod),
        id_xpath='//t:msDesc/@xml:id')
    tokenizer_layer = Tokenizer(
        milestone=milestone,
        normalisation=normalise(configmod),
        first_layer=True,
        id_xpath='//t:msDesc/@xml:id')
    for infile in fnmatch.filter (os.listdir (indir), '*tei.xml'):
        if verbose:
            print ("{}: milestone {} in file: {}".format (
                datetime.datetime.now().strftime ("%a, %d %b %Y %H:%M:%S %z"),
                milestone,
                infile,
            ))

        # get a witness name for display by removing file extensions
        witness_name = re.sub ('-merged', '', infile[:infile.find('.')])

        witness = extract_witness (
            xmlfile   = indir + '/' + infile,
            tokenizer = tokenizer_main
        )

        if witness is not None and witness.get('tokens'):
            witnesses.append(witness)
            logging.info ('milestone <%s> found in witness file <%s>' % (
                milestone,
                infile,
            ))
            # Get the layer witness too
            layerwit = extract_witness(
                xmlfile   = indir + '/' + infile,
                tokenizer = tokenizer_layer
            )
            layerwit['id'] += " (a.c.)"
            witnesses.append(layerwit)
            # Note the length of the (main) witness
            mslength.append(len(witness.get('tokens')))
        else:
            logging.info ('milestone <%s> not found in witness file <%s>' % (
                milestone,
                infile,
            ))
            missing.append(witness_name)

    # warn and exclude if one of the witnesses seems weirdly longer than
    # the others; it probably indicates a missing milestone marker and can
    # cause SVG generation to hang.
    msmedian = statistics.median(mslength)
    collation = {"witnesses": []}
    for wit in witnesses:
        if len(wit.get('tokens')) > msmedian + 800:
            print("Witness %s seems too long; excluding it from collation" % wit.get('id'),
                    file=sys.stderr)
        else:
            collation.get("witnesses").append(wit)

    # note on output which files are missing milestones
    if verbose and len(missing) > 0:
        print ("{}: milestone {} not in witnesses: {}".format (
            datetime.datetime.now().strftime ("%a, %d %b %Y %H:%M:%S %z"),
            milestone,
            ' '.join (missing),
        ))
    return collation


def extract_witness (**kwa):
    """ returns json
    """

    xmlfile   = kwa.get ('xmlfile')
    tokenizer = kwa.get ('tokenizer')

    try:
        with open (xmlfile, encoding = 'utf-8') as fh:
            return tokenizer.from_string (fh.read())
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

            with open (outfile, 'w', encoding='utf-8') as fh:
                json.dump (
                    c,
                    fh,
                    ensure_ascii = False,
                    indent = 4,
                    check_circular = True,
                )
