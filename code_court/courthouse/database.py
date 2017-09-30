import os
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db_uri = os.getenv("CODE_COURT_DB_URI") or "sqlite:////tmp/code_court.db"
engine = create_engine(db_uri, convert_unicode=True)

try:
    import uwsgi
    scopefunc = uwsgi.worker_id
except ImportError:
    scopefunc = threading.get_ident

db_session = scoped_session(sessionmaker(autocommit=False,
                                     autoflush=False,
                                     bind=engine), scopefunc=scopefunc)
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import model
    Base.metadata.create_all(bind=engine)

