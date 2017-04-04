import logging
import subprocess


def run (cmd):
    """ run command cmd and log in case of error
    """

    logging.basicConfig (
        format = '%(asctime)s %(message)s',
        filename = './command.log',
    )

    cp = subprocess.run (  # ISA CompletedProcess
        cmd,
        stdout  = subprocess.PIPE,
        stderr  = subprocess.PIPE,
        timeout = 60,  # raises TimeoutExpired
    )

    if cp.returncode:
        logging.error ('returncode: %s' % cp.returncode)
        logging.error ('stdout: %s' % cp.stdout)
        logging.error ('stderr: %s' % cp.stderr)
    else:
        logging.debug ('stdout: %s' % cp.stdout)
        logging.debug ('stderr: %s' % cp.stderr)

    return dict (
        returncode = cp.returncode,
        stdout = cp.stdout,
        stderr = cp.stderr,
    )
