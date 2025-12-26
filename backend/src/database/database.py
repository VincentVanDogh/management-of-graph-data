from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# TODO: Enter your password here
DATABASE_URL = "postgresql+psycopg2://postgres:<PASSWORD>@localhost:5432/mydb"
# or sqlite for testing:
# DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()
