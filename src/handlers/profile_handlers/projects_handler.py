from aiogram.types import CallbackQuery, Message
from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from src.keyboards.profile_keyboard import get_create_profile_keyboard
from src.states.profile_states.projects_state import ProjectsState
from aiogram.fsm.context import FSMContext



configure_logging()
logger = logging.getLogger(__name__)



async def add_projects(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.edit_text("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.projects:
                await state.set_state(ProjectsState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_text(
                    f"Your current projects are: {profile.projects}\n"
                    "Would you like to update them? (yes/no)"
                )
            else:
                await state.set_state(ProjectsState.waiting_for_projects)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_text(
                    "Please describe your projects. You can include:\n\n"
                    "• Project name and purpose\n"
                    "• Technologies used\n"
                    "• Your role and responsibilities\n"
                    "• Key achievements or outcomes\n"
                    "• Links to repositories or live demos\n\n"
                    "Tips:\n"
                    "• Be specific about your contributions\n"
                    "• Highlight the most impressive projects\n"
                    "• Include both personal and professional projects"
                )

    except Exception as ex:
        logger.error(f"Error in add_projects: {ex}")
        await callback.message.edit_text("❌ An error occurred. Please try again.")





async def process_adding_projects(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        if current_state == ProjectsState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(ProjectsState.waiting_for_projects)
                bot_message = await message.answer(
                    "Please describe your projects. You can include:\n\n"
                    "• Project name and purpose\n"
                    "• Technologies used\n"
                    "• Your role and responsibilities\n"
                    "• Key achievements or outcomes\n"
                    "• Links to repositories or live demos"
                )
                await state.update_data(last_bot_message=bot_message.message_id)
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("Projects update cancelled.", reply_markup=get_create_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

        projects = message.text.strip()
        
        if not projects:
            bot_message = await message.answer(
                "Please provide a description of your projects.\n"
                "You can include details about the project, technologies used, and your role."
            )
            await state.update_data(last_bot_message=bot_message.message_id)
            return
            
        if len(projects) > 1000:
            bot_message = await message.answer(
                "❌ Your message is too long. Please keep it under 1000 characters.\n"
                "Try to be more concise with your project descriptions.\n\n"
                "Focus on:\n"
                "• Project name and purpose\n"
                "• Technologies used\n"
                "• Your role and responsibilities\n"
                "• Key achievements or outcomes"
            )
            await state.update_data(last_bot_message=bot_message.message_id)
            return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                bot_message = await message.answer("❌ User not found. Please create a profile first.")
                await state.update_data(last_bot_message=bot_message.message_id)
                return

            profile = await Profile.update_profile(
                user_id=user.id,
                update_data={"projects": projects},
                session=session
            )

            if profile:
                bot_message = await message.answer(
                    f"✅ Your projects have been saved!\n\nProjects:\n{projects}",
                    reply_markup=get_create_profile_keyboard()
                )
                await state.update_data(last_bot_message=bot_message.message_id)
            else:
                bot_message = await message.answer(
                    "❌ Sorry, there was an error saving your projects. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )
                await state.update_data(last_bot_message=bot_message.message_id)

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing projects input: {ex}")
        bot_message = await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )
        await state.update_data(last_bot_message=bot_message.message_id)
        await state.clear()
