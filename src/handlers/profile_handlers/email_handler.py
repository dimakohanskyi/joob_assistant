from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging
import re

from src.databese.models import User
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.profile_keyboard import get_create_profile_keyboard, get_email_confirmation_keyboard
from src.states.profile_states.email_state import EmailState




configure_logging()
logger = logging.getLogger(__name__)



def is_valid_email(email: str) -> bool:
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))






async def add_email(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.edit_caption(
                    caption="❌ User not found. Please create a profile first.",
                    reply_markup=get_create_profile_keyboard()
                )
                return

            if user.user_login:
                await state.set_state(EmailState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption=f"Your current email is: {user.user_login}\n"
                    "Would you like to update it?",
                    reply_markup=get_email_confirmation_keyboard()
                )
            else:
                await state.set_state(EmailState.waiting_for_email)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption="Please enter your email address.\n\n"
                    "Example:\n"
                    "john.doe@example.com\n\n"
                    "Tips:\n"
                    "• Make sure to enter a valid email address\n"
                    "• The email should be your professional email",
                    reply_markup=get_create_profile_keyboard()
                )

    except Exception as ex:
        logger.error(f"Error in add_email: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )





async def process_email_confirmation(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == "confirm_email_update":
            await state.set_state(EmailState.waiting_for_email)
            await callback.message.edit_caption(
                caption="Please enter your email address.\n\n"
                "Example:\n"
                "john.doe@example.com",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "cancel_email_update":
            await state.clear()
            await callback.message.edit_caption(
                caption="Email update cancelled.",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "create_profile":
            await state.clear()
            await callback.message.edit_caption(
                caption="Profile Management",
                reply_markup=get_create_profile_keyboard()
            )

    except Exception as ex:
        logger.error(f"Error in process_email_confirmation: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )






async def process_adding_email(message: Message, state: FSMContext):
    try:
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        # Delete user's message
        await message.delete()
        
        email = message.text.strip()
        
        if not email:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="Please enter your email address.\n"
                "Example: john.doe@example.com",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        if not is_valid_email(email):
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Invalid email format. Please enter a valid email address.\n\n"
                "Example:\n"
                "john.doe@example.com",
                reply_markup=get_create_profile_keyboard()
            )
            return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ User not found. Please create a profile first.",
                    reply_markup=get_create_profile_keyboard()
                )
                return

            # Update user's email
            user.user_login = email
            await session.commit()
            await session.refresh(user)

            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption=f"✅ Your email has been updated!\nEmail: {email}",
                reply_markup=get_create_profile_keyboard()
            )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing email input: {ex}")
        try:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Sorry, something went wrong. Please try again.",
                reply_markup=get_create_profile_keyboard()
            )
        except Exception as edit_ex:
            logger.error(f"Error editing message: {edit_ex}")
        await state.clear()
