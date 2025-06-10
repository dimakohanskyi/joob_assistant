from aiogram.fsm.state import StatesGroup, State



class ProjectsState(StatesGroup):
    waiting_for_projects = State()
    waiting_for_update_confirmation = State()
