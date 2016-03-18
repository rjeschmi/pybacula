"""Helper functions working with the File table"""

import os
import sys
import argparse
import base64
import hashlib
from bacula.db.schema import Schema, File, FileName

def get_files_by_md5(md5, format="md5sum"):
    print "trying to find: %s" % md5
    md5_decoded = md5.decode('hex')
    md5_base64=base64.encodestring(md5_decoded).rstrip().rstrip('=')
    schema = Schema()
    session = schema.get_session()
    print "searching using: %s" % md5_base64
    files = session.query(File).filter(File.md5 == md5_base64).all()
    for file in files:
        print "found id: %s" % file.fileid
        print "file %s" % file
        print "filename: %s path: %s" % (file.filename.name, file.path.path)
        print "job: %s name: %s" % (file.jobid, file.job.name)

def generate_file_md5(filename, blocksize=2**20):
    m = hashlib.md5()
    with open( filename , "rb" ) as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update( buf )
    return m.hexdigest()

def get_files_by_name(name):
    schema = Schema()
    session = schema.get_session()
    filenames = session.query(FileName).filter(FileName.name == name).all()
    files = [ file for filename in filenames for file in filename.files ]

    print_files(files)

def print_files(files):
    for file in files:
        print "found id: %s" % file.fileid
        print "file %s" % file
        print "filename: %s path: %s" % (file.filename.name, file.path.path)
        print "job: %s name: %s" % (file.jobid, file.job.name)


def call_find(args):
    """The find caller"""
    for filename in args.filenames:
        if args.type == "name":
            get_files_by_name(filename)
        elif args.type == "md5":
            get_files_by_md5(filename)
        else:
            print "sorry don't know that query yet"


def set_options(subparser):
    file_parser = subparser.add_parser('file', help="Commands related to files")
    file_subparser = file_parser.add_subparsers(help="file subcommand help")
    find_parser = file_subparser.add_parser('find', help="find file")
    find_parser.add_argument('type', nargs="?", help="try searching by name")
    find_parser.add_argument('filenames', nargs="+", help='The positional arguments to work on')
    find_parser.set_defaults(func=call_find)

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
