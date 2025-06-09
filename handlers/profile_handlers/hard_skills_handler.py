from aiogram.types import CallbackQuery, Message
from databese.models import User, Profile
from databese.settings import get_db
from settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from keyboards.profile_keyboard import get_profile_keyboard
from states.hard_skills_state import HardSkillsState
from aiogram.fsm.context import FSMContext




configure_logging()
logger = logging.getLogger(__name__)



async def add_hard_skills(callback: CallbackQuery, state: FSMContext):
    try:
        async for session in get_db():
            user = await User.get_user(tg_user_id=callback.from_user.id, session=session)
            if not user:
                await callback.message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.get_user_profile(session=session, user_id=user.id)
            
            if profile and profile.hard_skills:
                await state.set_state(HardSkillsState.waiting_for_update_confirmation)
                await callback.message.answer(
                    f"Your current hard skills are: {profile.hard_skills}\n"
                    "Would you like to update them? (yes/no)"
                )
            else:
                await state.set_state(HardSkillsState.waiting_for_hard_skills)
                await callback.message.answer(
                    "Please enter your hard skills, separating each skill with a comma (,).\n\n"
                    "Example:\n"
                    "Python, SQL, Docker, Git, JavaScript, React, Node.js\n\n"
                    "Tips:\n"
                    "• Use commas to separate skills\n"
                    "• Keep each skill concise\n"
                    "• Focus on your strongest skills"
                )

    except Exception as ex:
        logger.error(f"Error in add_hard_skills: {ex}")
        await callback.message.answer("❌ An error occurred. Please try again.")







async def process_adding_hard_skills(message: Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        
        if current_state == HardSkillsState.waiting_for_update_confirmation:
            if message.text.lower() in ['yes', 'y']:
                await state.set_state(HardSkillsState.waiting_for_hard_skills)
                await message.answer(
                    "Please enter your new hard skills, separating each skill with a comma (,).\n\n"
                    "Example:\n"
                    "Python, SQL, Docker, Git, JavaScript, React, Node.js"
                )
            elif message.text.lower() in ['no', 'n']:
                await state.clear()
                await message.answer("Hard skills update cancelled.", reply_markup=get_profile_keyboard())
            else:
                await message.answer("Please answer with 'yes' or 'no'")
            return

        hard_skills = message.text.strip()
        
        if not hard_skills:
            await message.answer(
                "Please enter at least one hard skill.\n"
                "Example: Python, SQL, Docker"
            )
            return
            
        if len(hard_skills) > 500:
            await message.answer(
                "❌ Your message is too long. Please keep it under 500 characters.\n"
                "Try to be more concise with your skills.\n\n"
                "Example of good format:\n"
                "Python, SQL, Docker, Git, JavaScript, React, Node.js"
            )
            return
            
        skills_list = [skill.strip() for skill in hard_skills.split(',')]
        
        if len(skills_list) > 20:
            await message.answer(
                "❌ You've entered too many skills. Please limit to 20 skills maximum.\n"
                "Focus on your most important and relevant skills.\n\n"
                "Example of good format:\n"
                "Python, SQL, Docker, Git, JavaScript, React, Node.js"
            )
            return
            
        for skill in skills_list:
            if len(skill) > 50:
                await message.answer(
                    f"❌ The skill '{skill}' is too long. Please keep each skill under 50 characters.\n\n"
                    "Example of good format:\n"
                    "Python, SQL, Docker, Git, JavaScript, React, Node.js"
                )
                return
            if len(skill) < 2:
                await message.answer(
                    "❌ Each skill should be at least 2 characters long.\n\n"
                    "Example of good format:\n"
                    "Python, SQL, Docker, Git, JavaScript, React, Node.js"
                )
                return

        async for session in get_db():
            user = await User.get_user(tg_user_id=message.from_user.id, session=session)
            if not user:
                await message.answer("❌ User not found. Please create a profile first.")
                return

            profile = await Profile.update_profile(
                user_id=user.id,
                update_data={"hard_skills": hard_skills},
                session=session
            )

            if profile:
                await message.answer(
                    f"✅ Your hard skills have been saved!\nSkills: {hard_skills}",
                    reply_markup=get_profile_keyboard()
                )
            else:
                await message.answer(
                    "❌ Sorry, there was an error saving your hard skills. Please try again.",
                    reply_markup=get_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing hard skills input: {ex}")
        await message.answer(
            "❌ Sorry, something went wrong. Please try again.",
            reply_markup=get_profile_keyboard()
        )
        await state.clear()


