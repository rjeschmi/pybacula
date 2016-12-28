"""Helper functions working with the File table"""

import os
import sys
import re
import argparse
import base64
import hashlib
import logging
import pprint
from collections import Counter
from bacula.db.schema import Schema, File, FileName, Path, Job
from bacula.exceptions import PyBaculaException,FileNotFound

verbose = False
quiet = False
log = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)

class JobCache():
    """Implements a basic cache to speed up md5 comparisons"""
       
    def __init__(self, config):
        self.cache = {}
        self.schema = Schema(config)
        self.session = self.schema.get_session()

    def get_md5(self, md5):
        hits = []
        for job in self.cache:
            hit = self.cache[job].get(md5)
            if hit is not None:
                hits.append(hit)
            
        if len(hits)>0:
            log.debug("Returned hits: %s",  hits)
            return hits
        else:
            return None

    def cache_jobs(self, jobs):
        print "caching jobs: %s " % jobs
        uncached_jobs = []
        for job in jobs:
            if self.cache.get(job):
                pass
            else:
                self.cache[job]={}
                uncached_jobs.append(job)

        FileNameSession=self.session.query(File).\
            join(Path).\
            join(FileName).\
            join(Job).\
            filter(Job.jobid.in_(uncached_jobs))

        files=FileNameSession.all()
        for file in files:
            log.debug("caching jobid: %s md5: %s file: %s", file.jobid, file.md5, file)
            self.cache[file.jobid][file.md5]=file



class FileCMD():

  def __init__(self, config):
    self.schema = Schema(config)
    self.session = self.schema.get_session()
    self.cache = JobCache(config)
    self.stats = { 
        'jobs': Counter(),
        'found': 0,
        'notfound': Counter(),
    }

  def get_files_by_md5(self, md5, format="md5sum", use_cache=False, path=None):
    #print "trying to find: %s" % md5
    if os.path.isfile(md5):
        md5_hex=self.generate_file_md5(md5)
    else:
        md5_hex=md5
    md5_decoded = md5_hex.decode('hex')
    md5_base64=base64.encodestring(md5_decoded).rstrip().rstrip('=')
    log.debug("searching using: %s", md5_base64)
    files = []
    log.debug("got use_cache: %s", use_cache)
    if use_cache:
        #This will only be sure to get at least one job
        cache_hits = self.cache.get_md5(md5_base64) 
        if cache_hits is not None:
            log.debug("cache hit for md5: %s", md5)
            files = cache_hits
        
        else:
            log.debug("cache miss for md5: %s", md5)
            files = self.session.query(File).filter(File.md5 == md5_base64).all()
            jobs = []
            if len(files)==0 :
                print "This file is not in the database %s, %s" % (md5, path)
            else:
                for file in files:
                    jobs.append(file.jobid)
                    log.info("File matched: %s %s", file.path.path,file.filename.name)
                    log.info("Job matched: %s %s %s", file.job.jobid, file.job.job, file.job.name)
                log.debug("cache jobs for jobs: %s", jobs)
                cache.cache_jobs(jobs)

    else: 
        log.debug("not using cache")
        log.debug("session: %s" % self.session)
        files = self.session.query(File).filter(File.md5 == md5_base64).all()
        log.debug("got files: %s", len(files))
    if len(files) > 0 :
        for file in files:
            self.stats['jobs'][file.jobid]+=1
            if not quiet: 
                print "found id: %s filename: %s path: %s" % (file.fileid, file.filename.name, file.path.path)
                #print "file %s" % file
                print "\tjob: %s name: %s poolid: %s pool: %s" % (file.jobid, file.job.name, file.job.pool.poolid, file.job.pool.name)
    else:
        print "Can't find file in database with md5: %s" % md5_base64
        return None

  def generate_file_md5(self,filename, blocksize=2**20):
    m = hashlib.md5()
    log.debug("opening file: %s", filename)
    with open( filename , "rb" ) as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update( buf )
    return m.hexdigest()

  def get_files_by_name(self, name):
    filenames = self.session.query(FileName).filter(FileName.name == name).all()
    files = [ file for filename in filenames for file in filename.files ]

    self.print_files(files)

  def get_files_by_hashdeep(self, filename):
    """iterate through a hashdeep file and search by md5"""
    with open( filename) as fh:
        for line in fh:
            if line[0] == '%':
                pass
            elif line[0] == '#':
                pass
            else:
                hashfields = line.split(',')
                get_files_by_md5(hashfields[1], path=hashfields[3])

  def get_files_by_md5sum(self, filename, use_cache=False):
    """iterate through a md5sum file and search by md5"""
    with open( filename) as fh:
        for line in fh:
            m = re.match('(^[a-z0-9]{32})\s+(.*)$', line)
            if line[0] == '%':
                pass
            elif line[0] == '#' or line[0] == " ":
                pass
            elif m:
                log.debug("got line: %s", line)
                log.debug("calling get file by md5, use_cache: %s, path: %s", use_cache, m.group(2))
                try:
                    self.get_files_by_md5(m.group(1), use_cache=use_cache, path=m.group(2))
                except FileNotFound:
                    self.stats['notfound'].update([m.group(2)])
            else:
                print "didn't match line: %s" % line
        print "notfound: "
        pp.pprint( self.stats['notfound'])

  def print_files(self, files):
    for file in files:
        print "found id: %s" % file.fileid
        print "file %s" % file
        print "filename: %s path: %s" % (file.filename.name, file.path.path)
        print "job: %s name: %s" % (file.jobid, file.job.name)


def call_find(args, config=False):
    """The find caller"""
    log.info("call_find")
    global verbose, quiet
    if args.verbose == True:
        log.debug("found verbose args: %s", args)
        verbose = True
    if args.quiet == True:
        quiet = True
    file = FileCMD(config)
    for filename in args.filenames:
        if args.type == "name":
            file.get_files_by_name(filename)
        elif args.type == "md5":
            log.debug("calling get files by md5 cache: %s", args.cache)
            result = file.get_files_by_md5(filename, use_cache=args.cache)
            if result is None:
                print "Couldn't find %s in database" % filename
        elif args.type == "hashdeep":
            file.get_files_by_hashdeep(filename)
        elif args.type == "md5sum":
            file.get_files_by_md5sum(filename, use_cache=args.cache)
        else:
            print "sorry don't know that query yet: %s" % filename


def set_options(subparser):
    file_parser = subparser.add_parser('file', help="Commands related to files")
    file_subparser = file_parser.add_subparsers(help="file subcommand help")
    find_parser = file_subparser.add_parser('find', help="find file")
    find_parser.add_argument('type', nargs="?", help="Either name or md5 right now")
    find_parser.add_argument('--cache', help="Use the job cache", action='store_true')
    find_parser.add_argument('filenames', nargs="+", help='The positional arguments to work on')
    find_parser.set_defaults(func=call_find, cache=False)

def main(argv=None):
    """For commandline testing"""
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(description='This is the subcommand file')
    subparser = parser.add_subparsers(help="mock out subparsers since this would usually be called higher")
    set_options(subparser)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
