from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()
    

class InterviewResult(Base):
    __tablename__ = "interview_results"

    id = Column(Integer, primary_key=True)
    email = Column(String)
    answer = Column(String)
    result = Column(String)

    score = Column(Integer)   # 