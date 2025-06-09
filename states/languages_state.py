from aiogram.fsm.state import StatesGroup, State



class LanguagesState(StatesGroup):
    waiting_for_languages = State()
    waiting_for_update_confirmation = State()
