from aiogram.fsm.state import StatesGroup, State



class JobUrlState(StatesGroup):
    waiting_for_item_url = State()