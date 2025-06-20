from aiogram.types import Message, FSInputFile
from src.keyboards.main_keyboard import get_main_menu
from src.settings.logging_config import configure_logging
import logging
from src.databese.models import User
from src.databese.settings import get_db
from aiogram.fsm.context import FSMContext


configure_logging()
logger = logging.getLogger(__name__)




async def start_handler(message: Message, state: FSMContext):
    # Debug: Show last_bot_message value
    state_data = await state.get_data()
    last_bot_message_id = state_data.get('last_bot_message')
    await message.answer(f"last_bot_message: {last_bot_message_id}")
    
    bot_images_path = "media/images/joob_assistent_logo.png"

    base_caption = (
        "👋 Hey there! I'm **Joob Assistant** — your smart job-hunting buddy 💼🤖\n\n"
        "Here's what I can help you with:\n"
        "👤 Build your profile\n"
        "🔍 Analyze job posts with AI\n"
        "✉️ Generate custom cover letters\n"
        "📂 Track your applications\n"
        "📄 Save multiple CVs\n"
        "📊 Organize your job search like a pro\n\n"
        "Let's land your next job together! 🚀"
    )

    try:
        async for session in get_db():
            existing_user = await User.get_user(tg_user_id=message.from_user.id, session=session)

            if existing_user:
                welcome_message = "Welcome back! You're already logged in to **Joob Assistant**\n\n" + base_caption
            else:
                new_user = await User.create_new_user(
                    tg_user_id=message.from_user.id,
                    tg_user_name=message.from_user.username,
                    session=session
                )
                welcome_message = "Welcome to **Joob Assistant**! Your account has been created successfully\n\n" + base_caption

            await message.answer_photo(
                photo=FSInputFile(bot_images_path),
                caption=welcome_message,
                parse_mode="Markdown",
                reply_markup=get_main_menu()
            )
                
    except Exception as ex:
        logger.error("error with creating og getting user in start handler")

