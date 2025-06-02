from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from handlers.start_handler import start_handler




router = Router()
router.message.register(start_handler, CommandStart())
