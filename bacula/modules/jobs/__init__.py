"""Just set up options"""

import logging

log = logging.getLogger(__name__)

from bacula.modules.jobs import list as JobList

def call_list(args, config=False):
    """The list caller"""
    JobList.main(args, config)

def set_options(subparser):
    job_parser = subparser.add_parser('jobs', help="Commands related to jobs")
    job_subparser = job_parser.add_subparsers(help="jobs subcommands")
    jobs_list_parser = job_subparser.add_parser('list', help="get jobs")
    JobList.set_options(jobs_list_parser)
    jobs_list_parser.set_defaults(func=call_list)
