from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
from src.keyboards.profile_keyboard import get_create_profile_keyboard, get_soft_skills_confirmation_keyboard
from src.states.profile_states.soft_skills_state import SoftSkillsState




configure_logging()
logger = logging.getLogger(__name__)



async def add_soft_skills(callback: CallbackQuery, state: FSMContext):
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
            
            if profile and profile.soft_skills:
                await state.set_state(SoftSkillsState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption=f"Your current soft skills are: {profile.soft_skills}\n"
                    "Would you like to update them?",
                    reply_markup=get_soft_skills_confirmation_keyboard()
                )
            else:
                await state.set_state(SoftSkillsState.waiting_for_soft_skills)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption="Please enter your soft skills, separating each skill with a comma (,).\n\n"
                    "Example:\n"
                    "Communication, Leadership, Problem Solving, Teamwork, Time Management\n\n"
                    "Tips:\n"
                    "• Use commas to separate skills\n"
                    "• Keep each skill concise\n"
                    "• Focus on your strongest soft skills",
                    reply_markup=get_create_profile_keyboard()
                )

    except Exception as ex:
        logger.error(f"Error in add_soft_skills: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )









        


async def process_adding_soft_skills(message: Message, state: FSMContext):
    try:
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        # Delete user's message
        await message.delete()
        
        soft_skills = message.text.strip()
        
        if not soft_skills:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="Please enter at least one soft skill.\n"
                "Example: Communication, Leadership, Problem Solving",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        if len(soft_skills) > 500:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Your message is too long. Please keep it under 500 characters.\n"
                "Try to be more concise with your skills.\n\n"
                "Example of good format:\n"
                "Communication, Leadership, Problem Solving, Teamwork, Time Management",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        skills_list = [skill.strip() for skill in soft_skills.split(',')]
        
        if len(skills_list) > 20:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ You've entered too many skills. Please limit to 20 skills maximum.\n"
                "Focus on your most relevant and strongest soft skills.\n\n"
                "Example of good format:\n"
                "Communication, Leadership, Problem Solving, Teamwork, Time Management",
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
                    "Communication, Leadership, Problem Solving",
                    reply_markup=get_create_profile_keyboard()
                )
                return
            if len(skill) < 3:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Each skill should be at least 3 characters long.\n\n"
                    "Example of good format:\n"
                    "Communication, Leadership, Problem Solving",
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
                update_data={"soft_skills": soft_skills},
                session=session
            )

            if profile:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption=f"✅ Your soft skills have been updated!\nSkills: {soft_skills}",
                    reply_markup=get_create_profile_keyboard()
                )
            else:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Sorry, there was an error saving your soft skills. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing soft skills input: {ex}")
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


async def process_soft_skills_confirmation(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == "confirm_soft_skills_update":
            await state.set_state(SoftSkillsState.waiting_for_soft_skills)
            await callback.message.edit_caption(
                caption="Please enter your new soft skills, separating each skill with a comma (,).\n\n"
                "Example:\n"
                "Communication, Leadership, Problem Solving, Teamwork, Time Management",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "cancel_soft_skills_update":
            await state.clear()
            await callback.message.edit_caption(
                caption="Soft skills update cancelled.",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "create_profile":
            await state.clear()
            await callback.message.edit_caption(
                caption="Profile Management",
                reply_markup=get_create_profile_keyboard()
            )

    except Exception as ex:
        logger.error(f"Error in process_soft_skills_confirmation: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )
