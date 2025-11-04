from nicegui import ui
from app.api.api import api_session

def mostra_dati_account_page():
    user = api_session.user
    if not user:
        ui.label("Utente non autenticato").classes("text-negative")
        return

    with ui.card().classes('glass-card shadow-7 q-mt-xl').style('max-width:440px;min-width:340px;padding:44px 0 44px 0;'):
        ui.label("Dati Account").classes('glass-title').style("font-size:1.5em;")
        ui.label(f"Nome: {user.get('nome', '')}")
        ui.label(f"Cognome: {user.get('cognome', '')}")
        ui.label(f"Email: {user.get('email', '')}")
        ui.label(f"Ruolo: {user.get('ruolo', '').capitalize()}")