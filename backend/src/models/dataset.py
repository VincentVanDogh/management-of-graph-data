from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from database.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    content_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

from database.database import engine

Base.metadata.create_all(bind=engine)
