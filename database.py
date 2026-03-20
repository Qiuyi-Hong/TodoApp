import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("postgreSQLExternalAddress")
engine: Engine = create_engine(SQLALCHEMY_DATABASE_URL)  # type: ignore


SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = declarative_base()
