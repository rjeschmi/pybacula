#!/usr/bin/env python

import argparse
import logging
import pprint
from bacula.db.schema import Schema, Job, Media
from sqlalchemy.orm import lazyload, joinedload
from sets import Set
log = logging.getLogger(__name__) 

class List():
    
    def __init__(self, config):
        self.schema = Schema(config, debug=False)
        self.session = self.schema.get_session()

    def get_volumes(self, volumepattern, empty=False):
        log.debug("Calling with volumepattern[%s]", volumepattern)
        volumes = self.session.query(Media).options(
                            lazyload('*'),
                        ).filter(Media.volumename.like(volumepattern))
        if empty:
            volumes=volumes.filter(~Media.jobs.any())
        
        return volumes

    def get_jobs(self, volumepattern):
        log.debug("Calling with volumepattern[%s]", volumepattern)
        volumes = self.session.query(Media).options(
                            lazyload('*'),
                        ).filter(Media.volumename.like(volumepattern))
        jobset=Set()
        [ [ jobset.add(job.jobid)  for job in volume.jobs ] for volume in volumes if len(volume.jobs)>0 ]
        return list(jobset)

def main(args, config=False):
    """The main sub"""
    log.debug("Calling empty main wth volumepattern %s", args.volumepattern)
    volume_list = List(config)
    for volumepattern in args.volumepattern:
        if args.jobs:
            jobs = volume_list.get_jobs(volumepattern)
            print ",".join(str(x) for x in jobs)
        else:
            empty = args.empty
            volumes = volume_list.get_volumes(volumepattern, empty=empty)
            for volume in volumes:
                print args.template % volume.volumename
                for job in volume.jobs:
                    print args.jobtemplate % job.__dict__
                    if args.verbose:
                        pprint.pprint(job)
    

def set_options(subparser):
    subparser.add_argument('volumepattern', nargs="+", help="The volume pattern to search for empty")
    subparser.add_argument('--empty', help="List only empty volumes", action='store_true')
    subparser.add_argument('--jobs', help="output jobs matching volume pattern", action='store_true')
    subparser.add_argument('--template', help="output template", default='%s')
    subparser.add_argument('--jobtemplate', help="output template", default='%(jobid)s')
    subparser.add_argument('--verbose', help="output template", action='store_true')
    
if __name__ == "__main__":
    """We are being called from the command line"""
    parser = argparse.ArgumentParser(description='direct empty volumes call')
    set_options(parser)
    args = parser.parse_args()
    main(args, config=False)
