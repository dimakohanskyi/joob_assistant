from aiogram.types import Message, FSInputFile
from keyboards.main_keyboard import get_commands
from settings.logging_config import configure_logging
import logging
from databese.models import User
from databese.settings import get_db


configure_logging()
logger = logging.getLogger(__name__)




async def start_handler(message: Message):
    bot_images_path = "media/images/joob_assistent_logo.png"
    await message.answer_photo(
        photo=FSInputFile(bot_images_path),
        caption=(
            "👋 Hey there! I'm **Joob Assistant** — your smart job-hunting buddy 💼🤖\n\n"
            "Here's what I can help you with:\n"
            "👤 Build your profile\n"
            "🔍 Analyze job posts with AI\n"
            "✉️ Generate custom cover letters\n"
            "📂 Track your applications\n"
            "📄 Save multiple CVs\n"
            "📊 Organize your job search like a pro\n\n"
            "Let's land your next job together! 🚀"
        ),
        parse_mode="Markdown",
        reply_markup=get_commands()
    )

    logger.info(
        f"New user started bot - User ID: {message.from_user.id}, "
        f"Username: {message.from_user.username}, "
        f"First Name: {message.from_user.first_name}, "
        f"Last Name: {message.from_user.last_name}"
    )
    


#TODO
# 1. User Click on start 
# 2. check is this user in db 
# 3. if is show all commands plate and show login message
# 4. if not user with this id in database create new_one 



