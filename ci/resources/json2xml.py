#!/usr/bin/env python3

"""
Wrapper for tpen2tei.json2xml
"""

import argparse

import tpen2tei.json2xml


def metadata():
    """Return a dictionary suitable for the 'metadata' parameter to from_sc."""
    return {
        'title': 'Ժամանակագրութիւն',
        'author': 'Մատթէոս Ուռհայեցի',
        'short_error': True
    }

def special_chars():
    """Return a dictionary suitable for the 'special_chars parameter to from_sc."""
    return {
        'աշխարհ': ('asxarh', 'ARMENIAN ASHXARH SYMBOL'),
        'ամենայն': ('amenayn', 'ARMENIAN AMENAYN SYMBOL'),
        'արեգակն': ('aregakn', 'ARMENIAN AREGAKN SYMBOL'),
        'լուսին': ('lusin', 'ARMENIAN LUSIN SYMBOL'),
        'որպէս': ('orpes', 'ARMENIAN ORPES SYMBOL'),
        'երկիր': ('erkir', 'ARMENIAN ERKIR SYMBOL'),
        'երկին': ('erkin', 'ARMENIAN ERKIN SYMBOL'),
        'ընդ': ('und', 'ARMENIAN END SYMBOL'),
        'ըստ': ('ust', 'ARMENIAN EST SYMBOL'),
        'պտ': ('ptlig', 'ARMENIAN PEH-TIWN LIGATURE'),
        'թբ': ('tblig', 'ARMENIAN TO-BEN LIGATURE'),
        'թե': ('techlig', 'ARMENIAN TO-ECH LIGATURE'),
        'թի': ('tinilig', 'ARMENIAN TO-INI LIGATURE'),
        'թէ': ('tehlig', 'ARMENIAN TO-EH LIGATURE'),
        'էս': ('eslig', 'ARMENIAN EH-SEH LIGATURE'),
        'ես': ('echslig', 'ARMENIAN ECH-SEH LIGATURE'),
        'յր': ('yrlig', 'ARMENIAN YI-REH LIGATURE'),
        'րզ': ('rzlig', 'ARMENIAN REH-ZA LIGATURE'),
        'զմ': ('zmlig', 'ARMENIAN ZA-MEN LIGATURE'),
        'թգ': ('tglig', 'ARMENIAN TO-GIM LIGATURE'),
        'ա': ('avar', 'ARMENIAN AYB VARIANT'),
        'հ': ('hvar', 'ARMENIAN HO VARIANT'),
        'յ': ('yabove', 'ARMENIAN YI SUPERSCRIPT VARIANT')
    }

def numeric_parser():
    """Given the text content of a <num> element, try to turn it into a number."""

    def func (val):
        # Create the stack of characters
        sigfigs = [ord(c) for c in val.replace('և', '').upper() if ord(c) > 1328 and ord(c) < 1365]
        total = 0
        last = None
        for ch in sigfigs:
            # What is this one's numeric value?
            if ch < 1338:    # Ա-Թ
                chval = ch - 1328
            elif ch < 1347:  # Ժ-Ղ
                chval = (ch - 1337) * 10
            elif ch < 1356:  # Ճ-Ջ
                chval = (ch - 1346) * 100
            else:            # Ռ-Ք
                chval = (ch - 1355) * 1000

            # Put it in the total
            if last is None or chval < last:
                total += chval
            else:
                total *= chval
            last = chval
        return total

    return func

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

    tpen2tei.json2xml.json2xml (
        indir               = args.indir,
        outdir              = args.outdir,
        write_stdout_stderr = args.write_stdout_stderr,
        metadata            = metadata(),       # wants a dict
        special_chars       = special_chars(),  # wants a dict
        numeric_parser      = numeric_parser(), # wants a function
    )
