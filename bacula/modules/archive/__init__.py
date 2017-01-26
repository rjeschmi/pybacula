"""Just set up options"""

import logging

log = logging.getLogger(__name__)

from bacula.modules.archive import dump as JobDump

def call_archive(args, config=False):
    """The archive caller"""
    JobDump.main(args, config)

def set_options(subparser):
    job_parser = subparser.add_parser('archive', help="Commands related to archive")
    job_subparser = job_parser.add_subparsers(help="jobs subcommands")
    jobs_dump_parser = job_subparser.add_parser('dump', help="get jobs")
    JobDump.set_options(jobs_dump_parser)
    jobs_dump_parser.set_defaults(func=call_archive)
