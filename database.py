import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

load_dotenv()


try:
    SQLALCHEMY_DATABASE_URL = os.getenv("postgreSQLExternalAddress")
    engine: Engine = create_engine(SQLALCHEMY_DATABASE_URL)  # type: ignore
except Exception as e:
    print(f"Error creating engine: {e}")


SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine # type: ignore
)

Base = declarative_base()
