from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging
import re

from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.profile_keyboard import get_create_profile_keyboard, get_linkedin_confirmation_keyboard
from src.states.profile_states.linkedin_state import LinkedInState



configure_logging()
logger = logging.getLogger(__name__)



def is_valid_linkedin_url(url: str) -> bool:
    linkedin_pattern = r'^https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+/?$'
    return bool(re.match(linkedin_pattern, url))



async def add_linkedin(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.edit_caption(
                    caption="❌ User not found. Please create a profile first.",
                    reply_markup=get_create_profile_keyboard()
                )
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.user_linkedin:
                await state.set_state(LinkedInState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption=f"Your current LinkedIn URL is: {profile.user_linkedin}\n"
                    "Would you like to update it?",
                    reply_markup=get_linkedin_confirmation_keyboard()
                )
            else:
                await state.set_state(LinkedInState.waiting_for_linkedin)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption="Please enter your LinkedIn profile URL.\n\n"
                    "Example:\n"
                    "https://linkedin.com/in/username\n\n"
                    "Tips:\n"
                    "• Make sure to include the full URL\n"
                    "• The URL should be your public LinkedIn profile\n"
                    "• It should start with 'https://linkedin.com/in/'",
                    reply_markup=get_create_profile_keyboard()
                )

    except Exception as ex:
        logger.error(f"Error in add_linkedin: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )





async def process_linkedin_confirmation(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == "confirm_linkedin_update":
            await state.set_state(LinkedInState.waiting_for_linkedin)
            await callback.message.edit_caption(
                caption="Please enter your LinkedIn profile URL.\n\n"
                "Example:\n"
                "https://linkedin.com/in/username",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "cancel_linkedin_update":
            await state.clear()
            await callback.message.edit_caption(
                caption="LinkedIn URL update cancelled.",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "create_profile":
            await state.clear()
            await callback.message.edit_caption(
                caption="Profile Management",
                reply_markup=get_create_profile_keyboard()
            )

    except Exception as ex:
        logger.error(f"Error in process_linkedin_confirmation: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )





async def process_adding_linkedin(message: Message, state: FSMContext):
    try:
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        # Delete user's message
        await message.delete()
        
        linkedin_url = message.text.strip()
        
        if not linkedin_url:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="Please enter your LinkedIn profile URL.\n"
                "Example: https://linkedin.com/in/username",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        if not is_valid_linkedin_url(linkedin_url):
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Invalid LinkedIn URL format. Please enter a valid LinkedIn profile URL.\n\n"
                "Example:\n"
                "https://linkedin.com/in/username\n\n"
                "Make sure the URL:\n"
                "• Starts with https://linkedin.com/in/\n"
                "• Contains only letters, numbers, and hyphens in the username",
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

            profile = await Profile.update_profile(
                user_id=user.id,
                update_data={"user_linkedin": linkedin_url},
                session=session
            )

            if profile:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption=f"✅ Your LinkedIn URL has been updated!\nLinkedIn: {linkedin_url}",
                    reply_markup=get_create_profile_keyboard()
                )
            else:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Sorry, there was an error saving your LinkedIn URL. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing LinkedIn URL input: {ex}")
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
