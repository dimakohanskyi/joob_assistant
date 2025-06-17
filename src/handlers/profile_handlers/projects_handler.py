from aiogram.types import CallbackQuery, Message
from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from src.keyboards.profile_keyboard import get_create_profile_keyboard, get_projects_confirmation_keyboard
from src.states.profile_states.projects_state import ProjectsState
from aiogram.fsm.context import FSMContext



configure_logging()
logger = logging.getLogger(__name__)



async def add_projects(callback: CallbackQuery, state: FSMContext):
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
            
            if profile and profile.projects:
                await state.set_state(ProjectsState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption=f"Your current projects are: {profile.projects}\n"
                    "Would you like to update them?",
                    reply_markup=get_projects_confirmation_keyboard()
                )
            else:
                await state.set_state(ProjectsState.waiting_for_projects)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption="Please describe your projects. You can include:\n\n"
                    "• Project name and purpose\n"
                    "• Technologies used\n"
                    "• Your role and responsibilities\n"
                    "• Key achievements or outcomes\n"
                    "• Links to repositories or live demos\n\n"
                    "Tips:\n"
                    "• Be specific about your contributions\n"
                    "• Highlight the most impressive projects\n"
                    "• Include both personal and professional projects",
                    reply_markup=get_create_profile_keyboard()
                )

    except Exception as ex:
        logger.error(f"Error in add_projects: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )





async def process_projects_confirmation(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == "confirm_projects_update":
            await state.set_state(ProjectsState.waiting_for_projects)
            await callback.message.edit_caption(
                caption="Please describe your projects. You can include:\n\n"
                "• Project name and purpose\n"
                "• Technologies used\n"
                "• Your role and responsibilities\n"
                "• Key achievements or outcomes\n"
                "• Links to repositories or live demos",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "cancel_projects_update":
            await state.clear()
            await callback.message.edit_caption(
                caption="Projects update cancelled.",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "create_profile":
            await state.clear()
            await callback.message.edit_caption(
                caption="Profile Management",
                reply_markup=get_create_profile_keyboard()
            )

    except Exception as ex:
        logger.error(f"Error in process_projects_confirmation: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )





async def process_adding_projects(message: Message, state: FSMContext):
    try:
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        # Delete user's message
        await message.delete()
        
        projects = message.text.strip()
        
        if not projects:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="Please provide a description of your projects.\n"
                "You can include details about the project, technologies used, and your role.",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        if len(projects) > 1000:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Your message is too long. Please keep it under 1000 characters.\n"
                "Try to be more concise with your project descriptions.\n\n"
                "Focus on:\n"
                "• Project name and purpose\n"
                "• Technologies used\n"
                "• Your role and responsibilities\n"
                "• Key achievements or outcomes",
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
                update_data={"projects": projects},
                session=session
            )

            if profile:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption=f"✅ Your projects have been updated!\n\nProjects:\n{projects}",
                    reply_markup=get_create_profile_keyboard()
                )
            else:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Sorry, there was an error saving your projects. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing projects input: {ex}")
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
