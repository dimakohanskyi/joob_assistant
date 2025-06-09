from aiogram.fsm.state import StatesGroup, State



class EmailState(StatesGroup):
    waiting_for_email = State()
    waiting_for_update_confirmation = State()
