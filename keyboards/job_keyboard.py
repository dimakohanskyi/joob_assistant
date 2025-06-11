from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from databese.models import Jobb



def get_add_job_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Job URL", callback_data="add_job_url")],
        [InlineKeyboardButton(text="⭐ Priority", callback_data="add_job_priority")],
        [InlineKeyboardButton(text="📝 Status", callback_data="add_job_status")],
        [InlineKeyboardButton(text="🤖 AI Summary", callback_data="add_job_ai_summary")],
        [InlineKeyboardButton(text="📋 Additional Info", callback_data="add_job_additional_info")],
        [InlineKeyboardButton(text="⬅️ Back to Jobs", callback_data="main_menu")],
    ])
    return keyboard

def get_job_priority_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 High", callback_data="set_priority_high")],
        [InlineKeyboardButton(text="🟡 Medium", callback_data="set_priority_medium")],
        [InlineKeyboardButton(text="🟢 Low", callback_data="set_priority_low")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="job_keyboard")],
    ])
    return keyboard

def get_job_status_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Applied", callback_data="set_status_applied")],
        [InlineKeyboardButton(text="⏳ Waiting Response", callback_data="set_status_waiting_response")],
        [InlineKeyboardButton(text="❌ Rejected", callback_data="set_status_rejected")],
        [InlineKeyboardButton(text="👥 Interview 1", callback_data="set_status_interview_1")],
        [InlineKeyboardButton(text="👥 Interview 2", callback_data="set_status_interview_2")],
        [InlineKeyboardButton(text="🎉 Offer", callback_data="set_status_offer")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="job_keyboard")],
    ])
    return keyboard

