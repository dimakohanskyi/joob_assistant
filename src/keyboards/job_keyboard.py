from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_initial_job_keyboard():
    """Initial keyboard for adding a job URL"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Add Job URL", callback_data="add_job_url")],
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_menu")],
    ])
    return keyboard


def get_job_metadata_keyboard():
    """Keyboard for managing job metadata after URL is added"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ Set Priority", callback_data="add_job_priority")],
        [InlineKeyboardButton(text="📊 Set Status", callback_data="add_job_status")],
        [InlineKeyboardButton(text="🤖 Generate AI Summary", callback_data="add_job_ai_summary")],
        [InlineKeyboardButton(text="📝 Add Additional Info", callback_data="add_job_additional_info")],
        [InlineKeyboardButton(text="✅ Finish Adding Job", callback_data="finish_adding_job")],
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_menu")],
    ])
    return keyboard


def get_priority_keyboard():
    """Keyboard for selecting job priority"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 High", callback_data="set_priority_high")],
        [InlineKeyboardButton(text="🟡 Medium", callback_data="set_priority_medium")],
        [InlineKeyboardButton(text="🟢 Low", callback_data="set_priority_low")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="add_job_url")],
    ])
    return keyboard


def get_job_status_keyboard():
    """Keyboard for selecting job status"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Applied", callback_data="set_status_applied")],
        [InlineKeyboardButton(text="⏳ Waiting Response", callback_data="set_status_waiting_response")],
        [InlineKeyboardButton(text="❌ Rejected", callback_data="set_status_rejected")],
        [InlineKeyboardButton(text="🎯 Interview 1", callback_data="set_status_interview_1")],
        [InlineKeyboardButton(text="🎯 Interview 2", callback_data="set_status_interview_2")],
        [InlineKeyboardButton(text="✨ Offer", callback_data="set_status_offer")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="add_job_url")],
    ])
    return keyboard

