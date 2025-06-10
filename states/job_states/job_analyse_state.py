from aiogram.fsm.state import StatesGroup, State



class JobAnalyseState(StatesGroup):
    waiting_for_url = State()