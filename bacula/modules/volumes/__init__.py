"""Just set up options"""

import logging

log = logging.getLogger(__name__)

from bacula.modules.volumes import list as VolumeList

def call_list(args, config=False):
    """The list caller"""
    VolumeList.main(args, config)

def set_options(subparser):
    volume_parser = subparser.add_parser('volumes', help="Commands related to volumes")
    volume_subparser = volume_parser.add_subparsers(help="volumes subcommands")
    volume_get_vl_parser = volume_subparser.add_parser('list', help="get volumes")
    VolumeList.set_options(volume_get_vl_parser)
    volume_get_vl_parser.set_defaults(func=call_list)
