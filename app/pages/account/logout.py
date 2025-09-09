from nicegui import ui
from app.api.api import api_session

def logout_page():
    try:
        api_session.post('/auth/logout')
    except Exception:
        pass
    api_session.set_token(None)
    api_session.set_user(None)
    ui.notify('Logout effettuato', color='positive')
    ui.navigate.to('/')