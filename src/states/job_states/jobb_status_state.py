from aiogram.fsm.state import StatesGroup, State



class JobStatusState(StatesGroup):
    waiting_for_item_status = State()