from settings import Base
from sqlalchemy import Column, Text, String, TIMESTAMP, DateTime, ForeignKey, Integer, Float, Text, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime




class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    user_login = Column(String(55), unique=True, index=True)
    user_experience = Column(Float, default=0)
    user_languages = Column(JSONB)
    user_linkedin = Column(String(2048))
    user_git_hub = Column(String(2048))
    created_at = Column(DateTime, default=datetime.utcnow)



class UserProjects(Base):
    __tablename__ = "user_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_projects = Column(JSONB)




class Jobb:
    __tablename__ = "jobb"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048))
    status = Column(Enum('applied', 'waiting_response', 'rejected', 'interview_1', 'interview_2', 'offer', name='job_status'), default='')
    additional_info = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)





class JoobsItem:
    ...


class UserCV:
    ...


class UserCoverLetter:
    ... 

