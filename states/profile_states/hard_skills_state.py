from aiogram.fsm.state import StatesGroup, State



class HardSkillsState(StatesGroup):
    waiting_for_hard_skills = State()
    waiting_for_update_confirmation = State()
    