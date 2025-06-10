from aiogram.types import CallbackQuery, Message
from databese.models import User
from databese.settings import get_db
from settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from keyboards.profile_keyboard import get_create_profile_keyboard
from states.profile_states.email_state import EmailState
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
                await callback.message.answer("❌ User not found. Please create a profile first.")
                return

            if user.user_login:
                await state.set_state(EmailState.waiting_for_update_confirmation)
                await callback.message.answer(
                    f"Your current email is: {user.user_login}\n"
                    "Would you like to update it? (yes/no)"
                )
            else:
                await state.set_state(EmailState.waiting_for_email)
                await callback.message.answer(
                    "Please enter your email address.\n\n"
                    "Example:\n"
                    "john.doe@example.com\n\n"
                    "Tips:\n"
                    "• Make sure to enter a valid email address\n"
                    "• The email should be your professional email"
                )

    except Exception as ex:
        logger.error(f"Error in add_email: {ex}")
        await callback.message.answer("❌ An error occurred. Please try again.")


async def process_adding_email(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        
        if current_state == EmailState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(EmailState.waiting_for_email)
                await message.answer(
                    "Please enter your email address.\n\n"
                    "Example:\n"
                    "john.doe@example.com"
                )
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("Email update cancelled.", reply_markup=get_create_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

        email = message.text.strip()
        
        if not email:
            await message.answer(
                "Please enter your email address.\n"
                "Example: john.doe@example.com"
            )
            return
            
        if not is_valid_email(email):
            await message.answer(
                "❌ Invalid email format. Please enter a valid email address.\n\n"
                "Example:\n"
                "john.doe@example.com"
            )
            return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.answer("❌ User not found. Please create a profile first.")
                return

            # Update user's email
            user.user_login = email
            await session.commit()
            await session.refresh(user)

            await message.answer(
                f"✅ Your email has been saved!\nEmail: {email}",
                reply_markup=get_create_profile_keyboard()
            )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing email input: {ex}")
        await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )
        await state.clear()
