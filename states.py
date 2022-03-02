from aiogram.dispatcher.filters import state

class States(state.StatesGroup):
    Set_delta = state.State()
    Enter_months = state.State()
    Enter_weeks = state.State()
    Set_tokens = state.State()
    Set_tokens_from_user = state.State()

    Set_umoney = state.State()
    Set_tokens_for_tether = state.State()
    Set_payment_method = state.State()

    Admin = state.State()
    Set_user_id = state.State()
    Add_admin_message = state.State()
    Delete_admin_message = state.State()
    Add_tokens_for_user = state.State()
    Set_trend = state.State()
    Admin_send_message = state.State()

    Ignore_words = state.State()
    Ignore_no_words = state.State()
    Add_ignore_words = state.State()
    Del_ignore_words = state.State()