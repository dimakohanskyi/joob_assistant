from aiogram.fsm.state import StatesGroup, State



class CoverLetterState(StatesGroup):
    waiting_for_job_item_id = State()