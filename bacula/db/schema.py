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

    files = relationship("File", backref="job_ref", lazy="joined")
    poolid = Column(ForeignKey("pool.poolid"))
    pool = relationship("Pool")


class File(Base):
    """File class exposing file table"""
    __tablename__ = 'file'

    jobid = Column(ForeignKey("job.jobid"))
    filenameid = Column(ForeignKey("filename.filenameid"))
    pathid = Column(ForeignKey("path.pathid"))

    filename = relationship("FileName", back_populates="files", lazy="joined")
    path = relationship("Path", back_populates="files", lazy="joined")
    job = relationship("Job", lazy="joined")


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
    


class Schema(object):
    """The generic schema class"""
    __instance = None
    def __new__(cls, config=None):
        if Schema.__instance is None:
            Schema.__instance = object.__new__(cls)
        else:
            return Schema.__instance

        if config==None: 
            raise Exception("You need to define a config so we can get the db url")

        log.debug("create engine with url: %s", config.get('pybacula', 'db_url'))
        Schema.__instance.engine = create_engine(config.get('pybacula', 'db_url'), client_encoding='utf8')
        Base.prepare(Schema.__instance.engine, reflect=True)
        Schema.__instance.session = Session(Schema.__instance.engine)
        return Schema.__instance
    
    def __init__(self, config=None):
        """the init"""
        log.debug("calling init")

    def get_session(self):
        """return the Session object"""
        return self.session

    def get_engine(self):
        return self.engine
