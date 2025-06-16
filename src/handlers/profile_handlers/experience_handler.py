from aiogram.types import CallbackQuery, Message
from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from src.keyboards.profile_keyboard import get_create_profile_keyboard, get_experience_confirmation_keyboard
from src.states.profile_states.experience_state import ExperienceState
from aiogram.fsm.context import FSMContext



configure_logging()
logger = logging.getLogger(__name__)





async def add_experience(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.edit_caption(
                    caption="❌ User not found. Please create a profile first.",
                    reply_markup=get_create_profile_keyboard())
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.user_experience:
                await state.set_state(ExperienceState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption=f"Your current experience is {profile.user_experience} years.\n"
                    "Would you like to update it?",
                    reply_markup=get_experience_confirmation_keyboard()
                )
            else:
                await state.set_state(ExperienceState.waiting_for_experience)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption="Please enter your years of professional experience (e.g., 2.5 or 3):",
                )

    except Exception as ex:
        logger.error(f"Error in add_user_experience: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard())





async def process_experience_confirmation(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == "confirm_experience_update":
            await state.set_state(ExperienceState.waiting_for_experience)
            await callback.message.edit_caption(
                caption="Please enter your new years of experience:"
            )
        elif callback.data == "cancel_experience_update":
            await state.clear()
            await callback.message.edit_caption(
                caption="Experience update cancelled.",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "create_profile":
            await state.clear()
            await callback.message.edit_caption(
                caption="Profile Management",
                reply_markup=get_create_profile_keyboard()
            )
    except Exception as ex:
        logger.error(f"Error in process_experience_confirmation: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )






async def process_adding_experience(message: Message, state: FSMContext):
    try:
        await message.delete()
        
        try:
            experience = float(message.text)
            if experience < 0:
                await message.answer("Please enter a positive number for experience.")
                return
                
            if experience >= 100:
                await message.answer(
                    "Please enter a realistic number of years (less than 100).\n"
                    "For example: 2.5 or 15"
                )
                return
                
        except ValueError:
            await message.answer("Please enter a valid number (e.g., 2.5 or 3)")
            return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            if not profile:
                profile = Profile(user_id=user.id)
                session.add(profile)

            profile.user_experience = experience
            await session.commit()

            # Get the last bot message ID from state
            state_data = await state.get_data()
            last_bot_message_id = state_data.get('last_bot_message')
            
            if last_bot_message_id:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption=f"✅ Your experience of {experience} years has been saved!",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing experience input: {ex}")
        await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )
        await state.clear()