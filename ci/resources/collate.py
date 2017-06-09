import logging
import os
import fnmatch
import sys
import pprint
import argparse

from tpen2tei.wordtokenize import from_string


def milestones ():
    # grep --only-matching  --no-filename --regexp '<milestone unit="section" n=".*"/>' * | sort -u > milestones.txt

    return (
        "401",
        "407",
        "408",
        "410",
        "412",
        "418",
        "420",
        "421letter",
        "421",
        "424",
        "425",
        "432",
        "434",
        "437",
        "440",
        "446",
        "449",
        "452",
        "455",
        "460",
        "465",
        "470",
        "471",
        "471prophecy",
        "479",
        "480",
        "481",
        "483",
        "484",
        "485",
        "485prophecy",
        "486",
        "487",
        "489",
        "490",
        "492",
        "493",
        "494",
        "495",
        "496",
        "498",
        "499",
        "500",
        "500prologue",
        "502",
        "503",
        "504",
        "505",
        "507",
        "508",
        "511",
        "513",
        "514aftermath",
        "514confession",
        "514",
        "515",
        "516",
        "518",
        "519",
        "520",
        "521",
        "523",
        "525",
        "526",
        "528",
        "530",
        "532",
        "533",
        "534.2",
        "534",
        "535",
        "536",
        "538",
        "539",
        "540",
        "541",
        "542",
        "543",
        "544",
        "545",
        "546cutoff",
        "546",
        "547",
        "548",
        "549",
        "550bk3",
        "550",
        "550prologue",
        "551",
        "552",
        "553",
        "554",
        "555",
        "556",
        "557",
        "558",
        "559",
        "560",
        "561",
        "562",
        "563",
        "564",
        "566",
        "567",
        "568",
        "569",
        "570",
        "571",
        "572",
        "573",
        "574",
        "575",
        "576",
        "577",
        "585",
        "586",
        "589",
        "591",
        "592",
        "592thoros",
        "593",
        "594",
        "595barsegh",
        "595",
        "597",
        "598",
        "600",
        "602b",
        "602",
        "603",
        "604",
        "605",
        "606",
        "608",
        "609",
        "610",
        "611",
    )


def collate_em_all(**kwa):
    indir = kwa.get ('indir')
    outdir = kwa.get ('outdir')

    # collation = list (
    #     dict ( milestone = 401, witnesses = [ witness-1, witnesses-2, ..] ),
    #     dict ( milestone = 407, witnesses = [ witness-1, witnesses-2, ..] ),
    # )
    #
    collation = list()

    for milestone in milestones():
        ws = list()

        for infile in fnmatch.filter (os.listdir (indir), '*tei.xml'):

            collatex = tei2collatex (
                xmlfile   = indir + '/' + infile,
                milestone = milestone,
            )

            if collatex:
                ws.append (dict (
                    witness = infile,
                    data    = collatex,
                ))
                logging.info ('[%s:%s] wheee!' % (milestone, infile))
            else:
                logging.info ('[%s:%s] no data for CollateX' % (milestone, infile))

        collation.append (dict (
            milestone = milestone,
            witnesses = ws,
        ))

    return collation


def tei2collatex (**kwa):
    """ returns json
    """

    xmlfile   = kwa.get ('xmlfile')
    milestone = kwa.get ('milestone')

    try:
        with open (xmlfile, encoding = 'utf-8') as fh:
            return from_string (
                fh.read(),
                milestone    = milestone,
                first_layer  = False,
            )
    except FileNotFoundError:
        logging.info ('file not found: %s' % xmlfile)



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

    logging.basicConfig (
        format = '%(asctime)s %(message)s',
        filename = '%s.log' % os.path.basename (sys.argv[0]),
        level = logging.NOTSET,
    )

    args = parser.parse_args()

    with open ('./collation.json', 'w') as out:
        pprint.pprint (
            collate_em_all (
                indir = args.indir,
                outdir = args.outdir,
            ),
            out,
        )
