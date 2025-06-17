from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.profile_keyboard import get_create_profile_keyboard, get_hard_skills_confirmation_keyboard
from src.states.profile_states.hard_skills_state import HardSkillsState




configure_logging()
logger = logging.getLogger(__name__)



async def add_hard_skills(callback: CallbackQuery, state: FSMContext):
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
            
            if profile and profile.hard_skills:
                await state.set_state(HardSkillsState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption=f"Your current hard skills are: {profile.hard_skills}\n"
                    "Would you like to update them?",
                    reply_markup=get_hard_skills_confirmation_keyboard()
                )
            else:
                await state.set_state(HardSkillsState.waiting_for_hard_skills)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption="Please enter your hard skills, separating each skill with a comma (,).\n\n"
                    "Example:\n"
                    "Python, SQL, Docker, Git, JavaScript, React, Node.js\n\n"
                    "Tips:\n"
                    "• Use commas to separate skills\n" 
                    "• Keep each skill concise\n"
                    "• Focus on your strongest technical skills",
                    reply_markup=get_create_profile_keyboard()
                )

    except Exception as ex:
        logger.error(f"Error in add_hard_skills: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )



async def process_hard_skills_confirmation(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == "confirm_hard_skills_update":
            await state.set_state(HardSkillsState.waiting_for_hard_skills)
            await callback.message.edit_caption(
                caption="Please enter your new hard skills, separating each skill with a comma (,).\n\n"
                "Example:\n"
                "Python, SQL, Docker, Git, JavaScript, React, Node.js",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "cancel_hard_skills_update":
            await state.clear()
            await callback.message.edit_caption(
                caption="Hard skills update cancelled.",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "create_profile":
            await state.clear()
            await callback.message.edit_caption(
                caption="Profile Management",
                reply_markup=get_create_profile_keyboard()
            )

    except Exception as ex:
        logger.error(f"Error in process_hard_skills_confirmation: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )





async def process_adding_hard_skills(message: Message, state: FSMContext):
    try:
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        await message.delete()
        
        hard_skills = message.text.strip()
        
        if not hard_skills:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="Please enter at least one hard skill.\n"
                "Example: Python, SQL, Docker",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        if len(hard_skills) > 500:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Your message is too long. Please keep it under 500 characters.\n"
                "Try to be more concise with your skills.\n\n"
                "Example of good format:\n"
                "Python, SQL, Docker, Git, JavaScript, React, Node.js",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        skills_list = [skill.strip() for skill in hard_skills.split(',')]
        
        if len(skills_list) > 20:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ You've entered too many skills. Please limit to 20 skills maximum.\n"
                "Focus on your most relevant and strongest technical skills.\n\n"
                "Example of good format:\n"
                "Python, SQL, Docker, Git, JavaScript, React, Node.js",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        for skill in skills_list:
            if len(skill) > 50:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption=f"❌ The skill '{skill}' is too long. Please keep each skill under 50 characters.\n\n"
                    "Example of good format:\n"
                    "Python, SQL, Docker, Git, JavaScript, React, Node.js",
                    reply_markup=get_create_profile_keyboard()
                )
                return

            if len(skill) < 3:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Each skill should be at least 3 characters long.\n\n"
                    "Example of good format:\n"
                    "Python, SQL, Docker, Git, JavaScript, React, Node.js",
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
                update_data={"hard_skills": hard_skills},
                session=session
            )

            if profile:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption=f"✅ Your hard skills have been updated!\nSkills: {hard_skills}",
                    reply_markup=get_create_profile_keyboard()
                )
            else:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Sorry, there was an error saving your hard skills. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing hard skills input: {ex}")
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


