from aiogram.types import CallbackQuery, Message
from src.databese.models import User
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from src.keyboards.profile_keyboard import get_create_profile_keyboard
from src.states.profile_states.email_state import EmailState
from aiogram.fsm.context import FSMContext
import re



configure_logging()
logger = logging.getLogger(__name__)



def is_valid_email(email: str) -> bool:
    # Basic email validation pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))



async def add_email(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.edit_text("❌ User not found. Please create a profile first.")
                return

            if user.user_login:
                await state.set_state(EmailState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_text(
                    f"Your current email is: {user.user_login}\n"
                    "Would you like to update it? (yes/no)"
                )
            else:
                await state.set_state(EmailState.waiting_for_email)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_text(
                    "Please enter your email address.\n\n"
                    "Example:\n"
                    "john.doe@example.com\n\n"
                    "Tips:\n"
                    "• Make sure to enter a valid email address\n"
                    "• The email should be your professional email"
                )

    except Exception as ex:
        logger.error(f"Error in add_email: {ex}")
        await callback.message.edit_text("❌ An error occurred. Please try again.")


async def process_adding_email(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        if current_state == EmailState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(EmailState.waiting_for_email)
                bot_message = await message.answer(
                    "Please enter your email address.\n\n"
                    "Example:\n"
                    "john.doe@example.com"
                )
                await state.update_data(last_bot_message=bot_message.message_id)
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("Email update cancelled.", reply_markup=get_create_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

        email = message.text.strip()
        
        if not email:
            bot_message = await message.answer(
                "Please enter your email address.\n"
                "Example: john.doe@example.com"
            )
            await state.update_data(last_bot_message=bot_message.message_id)
            return
            
        if not is_valid_email(email):
            bot_message = await message.answer(
                "❌ Invalid email format. Please enter a valid email address.\n\n"
                "Example:\n"
                "john.doe@example.com"
            )
            await state.update_data(last_bot_message=bot_message.message_id)
            return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                bot_message = await message.answer("❌ User not found. Please create a profile first.")
                await state.update_data(last_bot_message=bot_message.message_id)
                return

            # Update user's email
            user.user_login = email
            await session.commit()
            await session.refresh(user)

            bot_message = await message.answer(
                f"✅ Your email has been saved!\nEmail: {email}",
                reply_markup=get_create_profile_keyboard()
            )
            await state.update_data(last_bot_message=bot_message.message_id)

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing email input: {ex}")
        bot_message = await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )
        await state.update_data(last_bot_message=bot_message.message_id)
        await state.clear()
