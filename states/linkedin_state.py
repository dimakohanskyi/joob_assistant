from aiogram.fsm.state import StatesGroup, State



class LinkedInState(StatesGroup):
    waiting_for_linkedin = State()
    waiting_for_update_confirmation = State()
