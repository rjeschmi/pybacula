#!/usr/bin/env python

import argparse
import logging

from bacula.db.schema import Schema, Job, Media
from sqlalchemy.orm import lazyload, joinedload
from sets import Set
log = logging.getLogger(__name__) 

class List():
    
    def __init__(self, config):
        self.schema = Schema(config, debug=False)
        self.session = self.schema.get_session()

    def get_jobs(self, pattern, args):
        log.debug("Calling with pattern[%s]", pattern)
        jobs = self.session.query(Job).options(
                            lazyload('*'),
                        ).filter(Job.name.like(pattern))
        if args.poolid>0:
            jobs.filter(Job.poolid==args.poolid)
        return jobs

def main(args, config=False):
    """The main sub"""
    log.debug("Calling empty main wth pattern %s", args.patterns)
    jobs_list = List(config)
    for pattern in args.patterns:
        if args.csv:
            jobset=Set()
            jobs = jobs_list.get_jobs(pattern, args)
            for job in jobs:
                jobset.add(job.jobid)
                
            print args.template % { 'id': ",".join(str(x) for x in jobset), 'name':pattern }
        elif args.volumes:
            jobs = jobs_list.get_jobs(pattern, args)
            for job in jobs:
                print args.template % job.__dict__
                for volume in job.volumes:
                    print '%s' % volume.volumename
        else:
            jobs = jobs_list.get_jobs(pattern, args)
            for job in jobs:
                print args.template % {'name':job.name, 'id':job.jobid}
    

def set_options(subparser):
    subparser.add_argument('patterns', nargs="+", help="The job pattern to search for empty")
    subparser.add_argument('--csv', help="list the jobs uniquely as comma separated", action="store_true")
    subparser.add_argument('--volumes', help="list the jobs and volumes", action="store_true")
    subparser.add_argument('--template', help="list the jobs with template default '%(name)s:%(jobid)s' job.name,job.jobid", default='%(name)s:%(jobid)s' )
    subparser.add_argument('--poolid', help="list the jobs uniquely as comma separated" )
    
if __name__ == "__main__":
    """We are being called from the command line"""
    parser = argparse.ArgumentParser(description='direct empty job call')
    set_options(parser)
    args = parser.parse_args()
    main(args, config=False)
