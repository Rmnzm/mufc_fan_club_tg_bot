from aiogram.filters.callback_data import CallbackData


class MatchDayCallbackFactory(CallbackData, prefix='watch_days'):
    id: int
