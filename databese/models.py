from databese.settings import Base
from sqlalchemy import Column, Text, String, TIMESTAMP, DateTime, ForeignKey, Integer, Float, Text, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import select
from datetime import datetime
import logging
from settings.logging_config import configure_logging

configure_logging()
logging = logging.getLogger(__name__)





class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    tg_user_name = Column(String(55))
    tg_user_id = Column(Integer, unique=True, index=True)
    user_login = Column(String(55), unique=True, index=True)
    user_experience = Column(Float, default=0)
    user_languages = Column(JSONB)
    user_linkedin = Column(String(2048))
    user_git_hub = Column(String(2048))
    created_at = Column(DateTime, default=datetime.utcnow)


    async def create_new_user(self, tg_user_id: int, tg_user_name: str, session):
        try:
            result = await session.execute(select(User).where(User.tg_user_id == tg_user_id))
            user = result.scalar()

            if user:
                return user
            else:
                new_user = User(
                    tg_user_name=tg_user_name,
                    tg_user_id=tg_user_id
                )
                session.add(new_user) 
                await session.commit()
                await session.refresh(new_user)
                return new_user
        except Exception as e:
            logging.error(f"Error creating user with id -- {tg_user_id}")
            await session.rollback()


    async def get_user(tg_user_id: int, session):
        try:
            result = await session.execute(select(User).where(User.tg_user_id == tg_user_id))
            user = result.scalar()
            return user
        except Exception as e:
            logging.error(f"Error to get user with id -- {tg_user_id}")










# class UserProjects(Base):
#     __tablename__ = "user_projects"
    
#     id = Column(Integer, primary_key=True, index=True)
#     user_projects = Column(JSONB)




# class Jobb:
#     __tablename__ = "jobb"

#     id = Column(Integer, primary_key=True, index=True)
#     url = Column(String(2048))
#     status = Column(Enum('applied', 'waiting_response', 'rejected', 'interview_1', 'interview_2', 'offer', name='job_status'), default='')
#     additional_info = Column(JSONB)
#     created_at = Column(DateTime, default=datetime.utcnow)





# class JoobsItem:
#     ...


# class UserCV:
#     ...


# class UserCoverLetter:
#     ... 

