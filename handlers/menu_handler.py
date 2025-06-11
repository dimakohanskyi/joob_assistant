from aiogram.types import CallbackQuery
from keyboards.main_keyboard import get_main_menu
from keyboards.job_keyboard import get_add_job_keyboard

async def main_menu_handler(callback: CallbackQuery):
    menu_message = "🏠 Main Menu"
    
    await callback.message.answer(
        text=menu_message,
        reply_markup=get_main_menu()
    ) 

async def get_add_menu_handler(callback: CallbackQuery):
    menu_message = "📝 Add New Job\n\nPlease select what information you want to add:"
    await callback.message.answer(
        text=menu_message,
        reply_markup=get_add_job_keyboard()
    ) 
