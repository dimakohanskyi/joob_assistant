from aiogram.fsm.state import StatesGroup, State



class JobAIAnalyseState(StatesGroup):
    waiting_for_url = State()