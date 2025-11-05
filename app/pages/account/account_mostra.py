from nicegui import ui
from app.api.api import api_session

def mostra_dati_account_page():
    user = api_session.user
    if not user:
        ui.label("Utente non autenticato").classes("text-negative")
        return

    ui.query('body').style('display:flex;justify-content:center;align-items:center;height:100vh;margin:0;')

    with ui.card().classes('glass-card shadow-9 q-mt-xl').style(
        'max-height:700px;min-height:500px;max-width:440px;min-width:340px;'
        'padding:44px 0;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:2.5em;background:#f0f0f0'
    ):
        # icon + title on the same line
        with ui.row().classes('items-center justify-center q-mb-lg'):
            ui.icon('account_circle').classes('glass-icon').style('background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%);'
    '-webkit-background-clip: text;'
    '-webkit-text-fill-color: transparent;'
    'font-size:5em;'
    'margin-right:10px;')
            ui.label("Dati Account").classes('glass-title').style(
                'color:#1976d2;text-align:center;font-size:2.5em;font-weight:bold;'
            )

        # user info labels
        ui.label(f"Nome: {user.get('nome', '')}").style(
            'background:#cadfeb;color:black;border-radius:1.8em;padding:.5em 3em;min-width:300px;display:block;text-align:center;'
        )
        ui.label(f"Cognome: {user.get('cognome', '')}").style(
            'background:#cadfeb;color:black;border-radius:1.8em;padding:.5em 3em;min-width:300px;display:block;text-align:center;'
        )
        ui.label(f"Email: {user.get('email', '')}").style(
            'background:#cadfeb;color:black;border-radius:1.8em;padding:.5em 3em;min-width:300px;display:block;text-align:center;'
        )
        ui.label(f"Ruolo: {user.get('ruolo', '').capitalize()}").style(
            'background:#cadfeb;color:black;border-radius:1.8em;padding:.5em 3em;min-width:300px;display:block;text-align:center;'
        )
