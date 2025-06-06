from aiogram.types import CallbackQuery
from databese.models import User
from databese.settings import get_db
from settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from keyboards.profile_keyboard import get_profile_keyboard



configure_logging()
logger = logging.getLogger(__name__)





async def create_account():
    ...
    