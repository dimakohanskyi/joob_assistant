from aiogram.types import CallbackQuery, Message
from databese.models import User, Profile
from databese.settings import get_db
from settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from keyboards.profile_keyboard import get_profile_keyboard
from states.education_state import EducationState
from aiogram.fsm.context import FSMContext



configure_logging()
logger = logging.getLogger(__name__)



async def add_education(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.education:
                await state.set_state(EducationState.waiting_for_update_confirmation)
                await callback.message.answer(
                    f"Your current education is: {profile.education}\n"
                    "Would you like to update it? (yes/no)"
                )
            else:
                await state.set_state(EducationState.waiting_for_education)
                await callback.message.answer(
                    "Please enter your education details, separating each entry with a comma (,).\n\n"
                    "Example:\n"
                    "Bachelor in Computer Science, University of Technology, 2018-2022\n"
                    "Master in Data Science, University of Science, 2022-2024\n\n"
                    "Tips:\n"
                    "• Use commas to separate different entries\n"
                    "• Include degree, institution, and years\n"
                    "• List your most recent education first"
                )

    except Exception as ex:
        logger.error(f"Error in add_education: {ex}")
        await callback.message.answer("❌ An error occurred. Please try again.")



async def process_adding_education(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        
        if current_state == EducationState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(EducationState.waiting_for_education)
                await message.answer(
                    "Please enter your new education details, separating each entry with a comma (,).\n\n"
                    "Example:\n"
                    "Bachelor in Computer Science, University of Technology, 2018-2022\n"
                    "Master in Data Science, University of Science, 2022-2024"
                )
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("Education update cancelled.", reply_markup=get_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

        education = message.text.strip()
        
        if not education:
            await message.answer(
                "Please enter at least one education entry.\n"
                "Example: Bachelor in Computer Science, University of Technology, 2018-2022"
            )
            return
            
        if len(education) > 1000:
            await message.answer(
                "❌ Your message is too long. Please keep it under 1000 characters.\n"
                "Try to be more concise with your education details.\n\n"
                "Example of good format:\n"
                "Bachelor in Computer Science, University of Technology, 2018-2022\n"
                "Master in Data Science, University of Science, 2022-2024"
            )
            return
            
        entries_list = [entry.strip() for entry in education.split('\n')]
        
        if len(entries_list) > 10:
            await message.answer(
                "❌ You've entered too many education entries. Please limit to 10 entries maximum.\n"
                "Focus on your most relevant education.\n\n"
                "Example of good format:\n"
                "Bachelor in Computer Science, University of Technology, 2018-2022\n"
                "Master in Data Science, University of Science, 2022-2024"
            )
            return
            
        for entry in entries_list:
            if len(entry) > 100:
                await message.answer(
                    f"❌ The entry '{entry}' is too long. Please keep each entry under 100 characters.\n\n"
                    "Example of good format:\n"
                    "Bachelor in Computer Science, University of Technology, 2018-2022"
                )
                return
            if len(entry) < 10:
                await message.answer(
                    "❌ Each education entry should be at least 10 characters long.\n\n"
                    "Example of good format:\n"
                    "Bachelor in Computer Science, University of Technology, 2018-2022"
                )
                return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.update_profile(
                user_id=user.id,
                update_data={"education": education},
                session=session
            )

            if profile:
                await message.answer(
                    f"✅ Your education details have been saved!\n\nEducation:\n{education}",
                    reply_markup=get_profile_keyboard()
                )
            else:
                await message.answer(
                    "❌ Sorry, there was an error saving your education details. Please try again.",
                    reply_markup=get_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing education input: {ex}")
        await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_profile_keyboard()
        )
        await state.clear()
