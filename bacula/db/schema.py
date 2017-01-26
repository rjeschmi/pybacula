"""Bacula Database Schema"""

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, relationship, subqueryload
from sqlalchemy import create_engine, ForeignKey, Column, Integer
import logging

log = logging.getLogger(__name__)

Base = automap_base()

class Job(Base):
    """Job class of bacula database"""
    __tablename__ = 'job'

    files = relationship("File", backref="job_ref", lazy="select")
    poolid = Column(ForeignKey("pool.poolid"))
    pool = relationship("Pool")
    volumes = relationship("Media", lazy="select", back_populates="jobs", secondary="jobmedia")

class File(Base):
    """File class exposing file table"""
    __tablename__ = 'file'

    jobid = Column(ForeignKey("job.jobid"))
    filenameid = Column(ForeignKey("filename.filenameid"))
    pathid = Column(ForeignKey("path.pathid"))

    filename = relationship("FileName", back_populates="files", lazy="select")
    path = relationship("Path", back_populates="files", lazy="select")
    job = relationship("Job", lazy="select")


class FileName(Base):
    __tablename__ = 'filename'

    filenameid = Column(Integer, primary_key=True)
    files = relationship("File", back_populates="filename")


class Path(Base):
    __tablename__ = 'path'

    pathid = Column(Integer, primary_key=True)
    files = relationship("File", back_populates="path")

class Pool(Base):
    __tablename__ = 'pool'

    poolid = Column(Integer, primary_key=True)

class Media(Base):
    __tablename__ = 'media'

    mediaid = Column(Integer, primary_key=True)
    jobs    = relationship("Job", back_populates="volumes", secondary="jobmedia")

class JobMedia(Base):
    __tablename__ = 'jobmedia'

    jobmediaid = Column(Integer, primary_key=True)
    mediaid = Column(ForeignKey("media.mediaid"))
    jobid = Column(ForeignKey("job.jobid"))

    media = relationship("Media" )
    job   = relationship("Job")

    


class Schema(object):
    """The generic schema class"""
    __instance = None
    def __new__(cls, config=None, debug=False):
        if Schema.__instance is None:
            Schema.__instance = object.__new__(cls)
        else:
            return Schema.__instance

        if config==None: 
            raise Exception("You need to define a config so we can get the db url")

        log.debug("create engine with url: %s", config.get('pybacula', 'db_url'))
        Schema.__instance.engine = create_engine(config.get('pybacula', 'db_url'), client_encoding='utf8', echo=debug)
        Base.prepare(Schema.__instance.engine, reflect=True)
        Schema.__instance.session = Session(Schema.__instance.engine)
        return Schema.__instance
    
    def __init__(self, config=None, debug=False):
        """the init"""
        log.debug("calling init")

    def get_session(self):
        """return the Session object"""
        return self.session

    def get_engine(self):
        return self.engine
