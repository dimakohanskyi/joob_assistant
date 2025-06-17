from aiogram.types import CallbackQuery, Message
from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from src.keyboards.profile_keyboard import get_create_profile_keyboard, get_github_confirmation_keyboard
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
                await callback.message.edit_caption(
                    caption="❌ User not found. Please create a profile first.",
                    reply_markup=get_create_profile_keyboard()
                )
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.user_git_hub:
                await state.set_state(GitHubState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption=f"Your current GitHub URL is: {profile.user_git_hub}\n"
                    "Would you like to update it?",
                    reply_markup=get_github_confirmation_keyboard()
                )
            else:
                await state.set_state(GitHubState.waiting_for_github)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption="Please enter your GitHub profile URL.\n\n"
                    "Example:\n"
                    "https://github.com/username\n\n"
                    "Tips:\n"
                    "• Make sure to include the full URL\n"
                    "• The URL should be your public GitHub profile",
                    reply_markup=get_create_profile_keyboard()
                )

    except Exception as ex:
        logger.error(f"Error in add_github: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )


async def process_github_confirmation(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == "confirm_github_update":
            await state.set_state(GitHubState.waiting_for_github)
            await callback.message.edit_caption(
                caption="Please enter your GitHub profile URL.\n\n"
                "Example:\n"
                "https://github.com/username",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "cancel_github_update":
            await state.clear()
            await callback.message.edit_caption(
                caption="GitHub URL update cancelled.",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "create_profile":
            await state.clear()
            await callback.message.edit_caption(
                caption="Profile Management",
                reply_markup=get_create_profile_keyboard()
            )

    except Exception as ex:
        logger.error(f"Error in process_github_confirmation: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )


async def process_adding_github(message: Message, state: FSMContext):
    try:
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        # Delete user's message
        await message.delete()
        
        github_url = message.text.strip()
        
        if not github_url:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="Please enter your GitHub profile URL.\n"
                "Example: https://github.com/username",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        if not is_valid_github_url(github_url):
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Invalid GitHub URL format. Please enter a valid GitHub profile URL.\n\n"
                "Example:\n"
                "https://github.com/username",
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
                update_data={"user_git_hub": github_url},
                session=session
            )

            if profile:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption=f"✅ Your GitHub URL has been updated!\nGitHub: {github_url}",
                    reply_markup=get_create_profile_keyboard()
                )
            else:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Sorry, there was an error saving your GitHub URL. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing GitHub URL input: {ex}")
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
