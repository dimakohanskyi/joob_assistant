from aiogram.fsm.state import StatesGroup, State



class JobUrlState(StatesGroup):
    waiting_for_item_url = State()
    waiting_for_additional_info = State()

    