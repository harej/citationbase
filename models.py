import credentials
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import url as url

Base = declarative_base()

engine_url = url.URL(
    drivername='mysql+pymysql',
    host='localhost',
    port=3306,
    username=credentials.db_user,
    password=credentials.db_pass,
    database=credentials.db_name,
    query={'charset': 'utf8'})

engine = create_engine(engine_url, encoding='utf-8')

class Page(Base):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    namespace = Column(Integer)
    title = Column(String(255))

class ExternalDB(Base):
    __tablename__ = 'externaldb'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    url_template = Column(String(255), nullable=False)

class RefString(Base):
    __tablename__ = 'refstring'
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, nullable=False)
    raw_string = Column(LargeBinary, nullable=False)

class RefRevision(Base):
    __tablename__ = 'refrevision'
    id = Column(Integer, primary_key=True)
    rev_id = Column(Integer, nullable=False)
    page_id = Column(Integer, nullable=False)
    rev_timestamp = Column(String(14), nullable=False)
    refstring_id = Column(Integer, ForeignKey('refstring.id'), nullable=False)

class RefParamName(Base):
    __tablename__ = 'refparamname'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))

class RefParamValue(Base):
    __tablename__ = 'refparamvalue'
    id = Column(Integer, primary_key=True)
    refstring_id = Column(Integer, ForeignKey('refstring.id'), nullable=False)
    refparamname_id = Column(Integer, ForeignKey('refparamname.id'), nullable=False)
    template_number = Column(Integer, nullable=False)
    value = Column(LargeBinary, nullable=False)

class RefMapping(Base):
    __tablename__ = 'refmapping'
    refstring_id = Column(Integer, ForeignKey('refstring.id'), primary_key=True)
    externaldb_id = Column(Integer, ForeignKey('externaldb.id'), primary_key=True)
    value = Column(String(255))

Base.metadata.create_all(engine)
