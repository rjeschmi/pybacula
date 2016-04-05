"""Where scripts are caled"""

import os
import sys
import argparse
import importlib
import logging

root_logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.debug("Logger set")


MODULES = [ '.file' ]

def bacula_cmd():
    args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose", action='store_true')
    subparser = parser.add_subparsers(help='sub command help')
    for module_name in MODULES:
        mod = importlib.import_module(module_name, package='bacula')
        mod.set_options(subparser)
    args = parser.parse_args()
    if(args.verbose):
        root_logger.setLevel(logging.DEBUG)
    logger.debug("Calling function: %s", args)
    args.func(args) 
