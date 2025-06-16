from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu():
    """Main menu keyboard with primary options"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Profile", callback_data="profile")],
        [InlineKeyboardButton(text="➕ Create / Update Profile", callback_data="create_account")],
        [InlineKeyboardButton(text="📝 Add Job", callback_data="job_keyboard")],
        [InlineKeyboardButton(text="📋 My Job Applications", callback_data="show_jobs")],
        [InlineKeyboardButton(text="📊 Job Analysis", callback_data="analyse_job_item")],
        [InlineKeyboardButton(text="✉️ Create Custom Cover Letter", callback_data="add_joob_item")],
        [InlineKeyboardButton(text="🔄 Get/Update Job Item", callback_data="get_job_item")],
    ])
    return keyboard


def get_profile_keyboard():
    """Profile view keyboard with back button"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_menu")],
    ])
    return keyboard


def get_create_profile_keyboard():
    """Create profile keyboard with back button"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="main_menu")],
    ])
    return keyboard