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
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    tg_user_name = Column(String(55))
    tg_user_id = Column(Integer, unique=True, index=True)
    user_login = Column(String(55), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


    @classmethod
    async def create_new_user(cls, tg_user_id: int, tg_user_name: str, session):
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


    @staticmethod
    async def get_user(tg_user_id: int, session):
        try:
            result = await session.execute(select(User).where(User.tg_user_id == tg_user_id))
            user = result.scalar()
            return user
        except Exception as e:
            logging.error(f"Error to get user with id -- {tg_user_id}")



class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True)
    user_experience = Column(Float, default=0)
    user_languages = Column(JSONB)
    user_linkedin = Column(JSONB)
    user_git_hub = Column(JSONB)
    hard_skills = Column(JSONB)
    soft_skills = Column(JSONB)
    education = Column(JSONB)
    projects = Column(JSONB)


    @classmethod
    async def update_profile(cls, user_id: int, update_data: dict, session):
        try:
            result = await session.execute(select(cls).where(cls.user_id == user_id))
            profile = result.scalar()
            
            if not profile:
                profile = cls(user_id=user_id)
                session.add(profile)
            
            for key, value in update_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            await session.commit()
            await session.refresh(profile)
            return profile
        except Exception as e:
            logging.error(f"Error updating profile for user_id {user_id}: {str(e)}")
            await session.rollback()
            return None






class Jobb:
    __tablename__ = "jobb_sheet"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048))
    status = Column(Enum('applied', 'waiting_response', 'rejected', 'interview_1', 'interview_2', 'offer', name='job_status'), default='')
    ai_summary = Column(Text)
    additional_info = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)







