from aiogram.fsm.state import StatesGroup, State



class EducationState(StatesGroup):
    waiting_for_education = State()
    waiting_for_update_confirmation = State()
