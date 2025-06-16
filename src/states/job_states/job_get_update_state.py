from aiogram.fsm.state import StatesGroup, State




class JobGetUpdateState(StatesGroup):
    waiting_for_item_id = State()
