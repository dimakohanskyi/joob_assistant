from aiogram.types import CallbackQuery, Message
from databese.models import User, Profile
from databese.settings import get_db
from settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from keyboards.profile_keyboard import get_profile_keyboard
from states.profile_states.experience_state import ExperienceState
from aiogram.fsm.context import FSMContext



configure_logging()
logger = logging.getLogger(__name__)





async def add_user_experience(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.user_experience:
                await state.set_state(ExperienceState.waiting_for_update_confirmation)
                await callback.message.answer(
                    f"Your current experience is {profile.user_experience} years.\n"
                    "Would you like to update it? (yes/no)"
                )
            else:
                await state.set_state(ExperienceState.waiting_for_experience)
                await callback.message.answer(
                    "Please enter your years of professional experience (e.g., 2.5 or 3):"
                )

    except Exception as ex:
        logger.error(f"Error in add_user_experience: {ex}")
        await callback.message.answer("❌ An error occurred. Please try again.")





async def process_experience_input(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        
        if current_state == ExperienceState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(ExperienceState.waiting_for_experience)
                await message.answer("Please enter your new years of experience:")
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("Experience update cancelled.", reply_markup=get_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

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

            await message.answer(
                f"✅ Your experience of {experience} years has been saved!",
                reply_markup=get_profile_keyboard()
            )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing experience input: {ex}")
        await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_profile_keyboard()
        )
        await state.clear()