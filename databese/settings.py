from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()



