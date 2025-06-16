from aiogram.types import CallbackQuery, Message
from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from src.keyboards.profile_keyboard import get_create_profile_keyboard
from src.states.profile_states.education_state import EducationState
from aiogram.fsm.context import FSMContext



configure_logging()
logger = logging.getLogger(__name__)



async def add_education(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.edit_text("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.education:
                await state.set_state(EducationState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_text(
                    f"Your current education is: {profile.education}\n"
                    "Would you like to update it? (yes/no)"
                )
            else:
                await state.set_state(EducationState.waiting_for_education)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_text(
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
        await callback.message.edit_text("❌ An error occurred. Please try again.")



async def process_adding_education(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        if current_state == EducationState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(EducationState.waiting_for_education)
                bot_message = await message.answer(
                    "Please enter your new education details, separating each entry with a comma (,).\n\n"
                    "Example:\n"
                    "Bachelor in Computer Science, University of Technology, 2018-2022\n"
                    "Master in Data Science, University of Science, 2022-2024"
                )
                await state.update_data(last_bot_message=bot_message.message_id)
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("Education update cancelled.", reply_markup=get_create_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

        education = message.text.strip()
        
        if not education:
            bot_message = await message.answer(
                "Please enter at least one education entry.\n"
                "Example: Bachelor in Computer Science, University of Technology, 2018-2022"
            )
            await state.update_data(last_bot_message=bot_message.message_id)
            return
            
        if len(education) > 1000:
            bot_message = await message.answer(
                "❌ Your message is too long. Please keep it under 1000 characters.\n"
                "Try to be more concise with your education details.\n\n"
                "Example of good format:\n"
                "Bachelor in Computer Science, University of Technology, 2018-2022\n"
                "Master in Data Science, University of Science, 2022-2024"
            )
            await state.update_data(last_bot_message=bot_message.message_id)
            return
            
        entries_list = [entry.strip() for entry in education.split('\n')]
        
        if len(entries_list) > 10:
            bot_message = await message.answer(
                "❌ You've entered too many education entries. Please limit to 10 entries maximum.\n"
                "Focus on your most relevant education.\n\n"
                "Example of good format:\n"
                "Bachelor in Computer Science, University of Technology, 2018-2022\n"
                "Master in Data Science, University of Science, 2022-2024"
            )
            await state.update_data(last_bot_message=bot_message.message_id)
            return
            
        for entry in entries_list:
            if len(entry) > 100:
                bot_message = await message.answer(
                    f"❌ The entry '{entry}' is too long. Please keep each entry under 100 characters.\n\n"
                    "Example of good format:\n"
                    "Bachelor in Computer Science, University of Technology, 2018-2022"
                )
                await state.update_data(last_bot_message=bot_message.message_id)
                return
            if len(entry) < 10:
                bot_message = await message.answer(
                    "❌ Each education entry should be at least 10 characters long.\n\n"
                    "Example of good format:\n"
                    "Bachelor in Computer Science, University of Technology, 2018-2022"
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
                update_data={"education": education},
                session=session
            )

            if profile:
                bot_message = await message.answer(
                    f"✅ Your education details have been saved!\n\nEducation:\n{education}",
                    reply_markup=get_create_profile_keyboard()
                )
                await state.update_data(last_bot_message=bot_message.message_id)
            else:
                bot_message = await message.answer(
                    "❌ Sorry, there was an error saving your education details. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )
                await state.update_data(last_bot_message=bot_message.message_id)

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing education input: {ex}")
        bot_message = await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )
        await state.update_data(last_bot_message=bot_message.message_id)
        await state.clear()
