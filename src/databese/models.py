from src.databese.settings import Base
from sqlalchemy import Column, Text, String, TIMESTAMP, DateTime, ForeignKey, Integer, Float, Text, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import select
from datetime import datetime
import logging
from src.settings.logging_config import configure_logging


configure_logging()
logging = logging.getLogger(__name__)



class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    tg_user_name = Column(String(55))
    tg_user_id = Column(Integer, unique=True, index=True)
    user_login = Column(String(55), unique=True, index=True)
    google_sheet_id = Column(String(100), unique=True, nullable=True)
    google_sheet_url = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    jobb_items = relationship("Jobb", back_populates="user", cascade="all, delete-orphan")


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

    user = relationship("User", back_populates="profile")


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


    @classmethod
    async def get_user_profile(cls, session, user_id: int):
        try:
            result = await session.execute(select(cls).where(cls.user_id == user_id))
            profile = result.scalar()
            if not profile:
                logging.error(f"Error with geting user profile for user with id - {user_id}")
                return
            return profile
        except Exception as ex:
            logging.error(f"Error geting user profile for user with id - {user_id}")
                



        

class Jobb(Base):
    __tablename__ = "jobb_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    priority = Column(Enum('high', 'medium', 'low', name="jobb_priority"), default="low")
    url = Column(String(2048))
    status = Column(Enum('applied', 'waiting_response', 'rejected', 'interview_1', 'interview_2', 'offer', name='job_status'), default='applied')
    ai_summary = Column(Text)
    additional_info = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="jobb_items")


    @staticmethod
    async def get_jobb_items(user_id, session):
        try:
            result = await session.execute(select(Jobb).where(Jobb.user_id == user_id))
            user_job_items = result.scalars().all()
            return user_job_items
        except Exception as ex:
            logging.error(f"Error getting job items: {str(ex)}")
            return []


    @staticmethod
    async def check_url_exists(session, user_id, url):
        try:
            result = await session.execute(
                select(Jobb).where(
                    Jobb.user_id == user_id,
                    Jobb.url == url
                )
            )
            existing_job = result.scalar_one_or_none()
            return existing_job is not None
        
        except Exception as ex:
            logging.error(f"Error checking URL existence: {str(ex)}")
            return False










