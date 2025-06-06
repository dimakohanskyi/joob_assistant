from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu():
    """Main menu keyboard with primary options"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 User Profile", callback_data="profile")],
        [InlineKeyboardButton(text="👤 Create Profile", callback_data="create_profile")],
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