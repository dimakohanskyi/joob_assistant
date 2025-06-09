from aiogram.types import CallbackQuery, Message
from databese.models import User, Profile
from databese.settings import get_db
from settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from keyboards.profile_keyboard import get_create_profile_keyboard
from states.linkedin_state import LinkedInState
from aiogram.fsm.context import FSMContext
import re



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
                await callback.message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.user_linkedin:
                await state.set_state(LinkedInState.waiting_for_update_confirmation)
                await callback.message.answer(
                    f"Your current LinkedIn URL is: {profile.user_linkedin}\n"
                    "Would you like to update it? (yes/no)"
                )
            else:
                await state.set_state(LinkedInState.waiting_for_linkedin)
                await callback.message.answer(
                    "Please enter your LinkedIn profile URL.\n\n"
                    "Example:\n"
                    "https://linkedin.com/in/username\n\n"
                    "Tips:\n"
                    "• Make sure to include the full URL\n"
                    "• The URL should be your public LinkedIn profile\n"
                    "• It should start with 'https://linkedin.com/in/'"
                )

    except Exception as ex:
        logger.error(f"Error in add_linkedin: {ex}")
        await callback.message.answer("❌ An error occurred. Please try again.")


async def process_adding_linkedin(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        
        if current_state == LinkedInState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(LinkedInState.waiting_for_linkedin)
                await message.answer(
                    "Please enter your LinkedIn profile URL.\n\n"
                    "Example:\n"
                    "https://linkedin.com/in/username"
                )
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("LinkedIn URL update cancelled.", reply_markup=get_create_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

        linkedin_url = message.text.strip()
        
        if not linkedin_url:
            await message.answer(
                "Please enter your LinkedIn profile URL.\n"
                "Example: https://linkedin.com/in/username"
            )
            return
            
        if not is_valid_linkedin_url(linkedin_url):
            await message.answer(
                "❌ Invalid LinkedIn URL format. Please enter a valid LinkedIn profile URL.\n\n"
                "Example:\n"
                "https://linkedin.com/in/username\n\n"
                "Make sure the URL:\n"
                "• Starts with https://linkedin.com/in/\n"
                "• Contains only letters, numbers, and hyphens in the username"
            )
            return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.update_profile(
                user_id=user.id,
                update_data={"user_linkedin": linkedin_url},
                session=session
            )

            if profile:
                await message.answer(
                    f"✅ Your LinkedIn URL has been saved!\nLinkedIn: {linkedin_url}",
                    reply_markup=get_create_profile_keyboard()
                )
            else:
                await message.answer(
                    "❌ Sorry, there was an error saving your LinkedIn URL. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing LinkedIn URL input: {ex}")
        await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )
        await state.clear()
