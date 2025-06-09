from aiogram.types import CallbackQuery, Message
from databese.models import User, Profile
from databese.settings import get_db
from settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from keyboards.profile_keyboard import get_create_profile_keyboard
from states.projects_state import ProjectsState
from aiogram.fsm.context import FSMContext



configure_logging()
logger = logging.getLogger(__name__)



async def add_projects(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.projects:
                await state.set_state(ProjectsState.waiting_for_update_confirmation)
                await callback.message.answer(
                    f"Your current projects are: {profile.projects}\n"
                    "Would you like to update them? (yes/no)"
                )
            else:
                await state.set_state(ProjectsState.waiting_for_projects)
                await callback.message.answer(
                    "Please describe your projects. You can include:\n\n"
                    "• Project name and purpose\n"
                    "• Technologies used\n"
                    "• Your role and responsibilities\n"
                    "• Key achievements or outcomes\n"
                    "• Links to repositories or live demos\n\n"
                    "Example:\n"
                    "E-commerce Platform: Developed a full-stack e-commerce solution using React and Node.js. "
                    "Implemented user authentication, payment processing, and inventory management. "
                    "Reduced checkout time by 40% and increased conversion rate by 25%.\n\n"
                    "Mobile Health App: Created a Flutter-based health tracking application with real-time data "
                    "synchronization and offline capabilities. Integrated with wearable devices and implemented "
                    "data visualization features."
                )

    except Exception as ex:
        logger.error(f"Error in add_projects: {ex}")
        await callback.message.answer("❌ An error occurred. Please try again.")





async def process_adding_projects(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        
        if current_state == ProjectsState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(ProjectsState.waiting_for_projects)
                await message.answer(
                    "Please describe your projects. You can include:\n\n"
                    "• Project name and purpose\n"
                    "• Technologies used\n"
                    "• Your role and responsibilities\n"
                    "• Key achievements or outcomes\n"
                    "• Links to repositories or live demos"
                )
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("Projects update cancelled.", reply_markup=get_create_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

        projects = message.text.strip()
        
        if not projects:
            await message.answer(
                "Please provide a description of your projects.\n"
                "You can include details about the project, technologies used, and your role."
            )
            return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.update_profile(
                user_id=user.id,
                update_data={"projects": projects},
                session=session
            )

            if profile:
                await message.answer(
                    f"✅ Your projects have been saved!\n\nProjects:\n{projects}",
                    reply_markup=get_create_profile_keyboard()
                )
            else:
                await message.answer(
                    "❌ Sorry, there was an error saving your projects. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing projects input: {ex}")
        await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )
        await state.clear()
