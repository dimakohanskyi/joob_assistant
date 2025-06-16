from aiogram.types import CallbackQuery, Message
from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from src.keyboards.profile_keyboard import get_create_profile_keyboard
from src.states.profile_states.git_hub_state import GitHubState
from aiogram.fsm.context import FSMContext
import re



configure_logging()
logger = logging.getLogger(__name__)



def is_valid_github_url(url: str) -> bool:
    github_pattern = r'^https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+/?$'
    return bool(re.match(github_pattern, url))



async def add_github(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.user_git_hub:
                await state.set_state(GitHubState.waiting_for_update_confirmation)
                await callback.message.answer(
                    f"Your current GitHub URL is: {profile.user_git_hub}\n"
                    "Would you like to update it? (yes/no)"
                )
            else:
                await state.set_state(GitHubState.waiting_for_github)
                await callback.message.answer(
                    "Please enter your GitHub profile URL.\n\n"
                    "Example:\n"
                    "https://github.com/username\n\n"
                    "Tips:\n"
                    "• Make sure to include the full URL\n"
                    "• The URL should be your public GitHub profile"
                )

    except Exception as ex:
        logger.error(f"Error in add_github: {ex}")
        await callback.message.answer("❌ An error occurred. Please try again.")


async def process_adding_github(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        
        if current_state == GitHubState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(GitHubState.waiting_for_github)
                await message.answer(
                    "Please enter your GitHub profile URL.\n\n"
                    "Example:\n"
                    "https://github.com/username"
                )
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("GitHub URL update cancelled.", reply_markup=get_create_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

        github_url = message.text.strip()
        
        if not github_url:
            await message.answer(
                "Please enter your GitHub profile URL.\n"
                "Example: https://github.com/username"
            )
            return
            
        if not is_valid_github_url(github_url):
            await message.answer(
                "❌ Invalid GitHub URL format. Please enter a valid GitHub profile URL.\n\n"
                "Example:\n"
                "https://github.com/username"
            )
            return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.update_profile(
                user_id=user.id,
                update_data={"user_git_hub": github_url},
                session=session
            )

            if profile:
                await message.answer(
                    f"✅ Your GitHub URL has been saved!\nGitHub: {github_url}",
                    reply_markup=get_create_profile_keyboard()
                )
            else:
                await message.answer(
                    "❌ Sorry, there was an error saving your GitHub URL. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing GitHub URL input: {ex}")
        await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )
        await state.clear()
