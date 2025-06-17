from aiogram.types import CallbackQuery, Message
from src.databese.models import User, Profile
from src.databese.settings import get_db
from src.settings.logging_config import configure_logging
import logging
from sqlalchemy import select
from src.keyboards.profile_keyboard import get_create_profile_keyboard, get_languages_confirmation_keyboard
from src.states.profile_states.languages_state import LanguagesState
from aiogram.fsm.context import FSMContext



configure_logging()
logger = logging.getLogger(__name__)



async def add_languages(callback: CallbackQuery, state: FSMContext):
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
            
            if profile and profile.user_languages:
                await state.set_state(LanguagesState.waiting_for_update_confirmation)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption=f"Your current languages are: {profile.user_languages}\n"
                    "Would you like to update them?",
                    reply_markup=get_languages_confirmation_keyboard()
                )
            else:
                await state.set_state(LanguagesState.waiting_for_languages)
                await state.update_data(last_bot_message=callback.message.message_id)
                await callback.message.edit_caption(
                    caption="Please enter your languages, separating each language with a comma (,).\n\n"
                    "Example:\n"
                    "English (Fluent), German (Intermediate), Norwegian (Basic)\n\n"
                    "Tips:\n"
                    "• Use commas to separate languages\n"
                    "• Include proficiency level in parentheses\n"
                    "• Common proficiency levels: Native, Fluent, Advanced, Intermediate, Basic",
                    reply_markup=get_create_profile_keyboard()
                )

    except Exception as ex:
        logger.error(f"Error in add_languages: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )





async def process_languages_confirmation(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.data == "confirm_languages_update":
            await state.set_state(LanguagesState.waiting_for_languages)
            await callback.message.edit_caption(
                caption="Please enter your languages, separating each language with a comma (,).\n\n"
                "Example:\n"
                "English (Fluent), German (Intermediate), Norwegian (Basic)",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "cancel_languages_update":
            await state.clear()
            await callback.message.edit_caption(
                caption="Languages update cancelled.",
                reply_markup=get_create_profile_keyboard()
            )
        elif callback.data == "create_profile":
            await state.clear()
            await callback.message.edit_caption(
                caption="Profile Management",
                reply_markup=get_create_profile_keyboard()
            )

    except Exception as ex:
        logger.error(f"Error in process_languages_confirmation: {ex}")
        await callback.message.edit_caption(
            caption="❌ An error occurred. Please try again.",
            reply_markup=get_create_profile_keyboard()
        )





async def process_adding_languages(message: Message, state: FSMContext):
    try:
        state_data = await state.get_data()
        last_bot_message_id = state_data.get('last_bot_message')
        
        # Delete user's message
        await message.delete()
        
        languages = message.text.strip()
        
        if not languages:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="Please enter at least one language.\n"
                "Example: English (Fluent), German (Intermediate)",
                reply_markup=get_create_profile_keyboard()
            )
            return
        
        #todo add validation on numbers 
            
        if len(languages) > 500:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ Your message is too long. Please keep it under 500 characters.\n"
                "Try to be more concise with your language entries.\n\n"
                "Example of good format:\n"
                "English (Fluent), German (Intermediate), Norwegian (Basic)",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        languages_list = [lang.strip() for lang in languages.split(',')]
        
        if len(languages_list) > 10:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_bot_message_id,
                caption="❌ You've entered too many languages. Please limit to 10 languages maximum.\n"
                "Focus on your most proficient languages.\n\n"
                "Example of good format:\n"
                "English (Fluent), German (Intermediate), Norwegian (Basic)",
                reply_markup=get_create_profile_keyboard()
            )
            return
            
        for lang in languages_list:
            if len(lang) > 50:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption=f"❌ The language entry '{lang}' is too long. Please keep each entry under 50 characters.\n\n"
                    "Example of good format:\n"
                    "English (Fluent), German (Intermediate), Norwegian (Basic)",
                    reply_markup=get_create_profile_keyboard()
                )
                return
            if len(lang) < 5:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Each language entry should be at least 5 characters long.\n\n"
                    "Example of good format:\n"
                    "English (Fluent), German (Intermediate), Norwegian (Basic)",
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
                update_data={"user_languages": languages},
                session=session
            )

            if profile:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption=f"✅ Your languages have been updated!\nLanguages: {languages}",
                    reply_markup=get_create_profile_keyboard()
                )
            else:
                await message.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=last_bot_message_id,
                    caption="❌ Sorry, there was an error saving your languages. Please try again.",
                    reply_markup=get_create_profile_keyboard()
                )

        await state.clear()

    except Exception as ex:
        logger.error(f"Error processing languages input: {ex}")
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
