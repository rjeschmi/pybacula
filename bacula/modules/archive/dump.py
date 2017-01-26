#!/usr/bin/env python

import os
import io
import argparse
import logging

from bareos.util.bareosbase64 import BareosBase64

from bacula.db.schema import Schema, Job, Media
from sqlalchemy.orm import lazyload, joinedload
from sets import Set
log = logging.getLogger(__name__) 

b64 = BareosBase64()

class ArchiveDump():
    
    def __init__(self, config):
        self.schema = Schema(config, debug=False)
        self.session = self.schema.get_session()
        self.manifest_template = config.get

    def get_job(self, jobid, args):
        log.debug("Calling with pattern[%s]", jobid)
        job = self.session.query(Job).options(
                            lazyload('*'),
                        ).filter(Job.jobid==jobid).first()
        return job

def main(args, config=False):
    """The main sub"""
    log.debug("Calling empty main wth pattern %s", args.jobids)
    jobs_dump = ArchiveDump(config)
    for jobid in args.jobids:
        job = jobs_dump.get_job(jobid, args)
        with io.open('manifest-%s-md5.txt' % jobid, 'w', encoding='utf-8') as manifest:
            for file in job.files:
                """create a manifest from a list of files"""
                if file.md5 != '0':
                    filename = os.path.join(file.path.path, file.filename.name)
                    md5hex = u"{0:033x}".format(b64.base64_to_int(file.md5))
                    manifest.write(u"{0}  {1}\n".format(md5hex[:32], filename))
            
        for volume in job.volumes:
            """also keep a record of the volumes used"""
        
    

def set_options(subparser):
    subparser.add_argument('jobids', nargs="+", help="The job pattern to search for empty")
    
if __name__ == "__main__":
    """We are being called from the command line"""
    parser = argparse.ArgumentParser(description='direct empty job call')
    set_options(parser)
    args = parser.parse_args()
    main(args, config=False)
