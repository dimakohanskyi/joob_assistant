from aiogram.types import CallbackQuery





async def profile_handler(callback: CallbackQuery):
    await callback.message.answer("DALBAYOB ya tyt")