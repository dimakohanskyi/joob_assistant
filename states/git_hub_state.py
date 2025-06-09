from aiogram.fsm.state import StatesGroup, State



class GitHubState(StatesGroup):
    waiting_for_github = State()
    waiting_for_update_confirmation = State()
