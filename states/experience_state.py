from aiogram.fsm.state import StatesGroup, State



class ExperienceState(StatesGroup):
    waiting_for_experience = State()
    waiting_for_update_confirmation = State()

    