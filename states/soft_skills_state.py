from aiogram.fsm.state import StatesGroup, State



class SoftSkillsState(StatesGroup):
    waiting_for_soft_skills = State()
    waiting_for_update_confirmation = State()
