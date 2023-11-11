# все состояния

from aiogram.fsm.state import State, StatesGroup


class HistoryStates(StatesGroup):
    setting_history = State()
    preparing_for_history = State()
    history_passing = State()
    quiz_passing_preparing = State()
    quiz_passing = State()
    quiz_ending = State()


class QuestsStates(StatesGroup):
    setting_quest = State()
    setting_team = State()
    creating_team_name = State()
    adding_to_team = State()
    preparing_for_quest = State()
    reading_quest = State()
    answering_quest = State()
