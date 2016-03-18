"""Bacula Database Schema"""

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, relationship, subqueryload
from sqlalchemy import create_engine, ForeignKey, Column, Integer

Base = automap_base()
ENGINE = create_engine('postgresql://bacula_ro:bacula_ro@127.0.0.1/bacula', client_encoding='utf8')

class Job(Base):
    """Job class of bacula database"""
    __tablename__ = 'job'

    files = relationship("File", backref="job_ref", lazy="joined")


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


class Schema():
    """The generic schema class"""

    def __init__(self):
        self.engine = ENGINE
        Base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)

    def get_session(self):
        """return the Session object"""
        return self.session
