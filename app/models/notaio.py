from nicegui import ui
from app.api.api import api_session
from app.components.components import header

def dettaglio_notaio_page():
    header("Profilo Notaio")
    res = api_session.get('/notai/me')
    if res.status_code == 200:
        notaio = res.json()
        utente = notaio.get('utente', {})
        ui.label(f"Nome: {utente.get('nome', '')}")
        ui.label(f"Cognome: {utente.get('cognome', '')}")
        ui.label(f"Email: {utente.get('email', '')}")
        ui.label(f"Codice Notarile: {notaio.get('codice_notarile', '')}")
        ui.label(f"Ruolo: NOTAIO")
        ui.button('Modifica Dati', on_click=lambda: ui.open('/profilo/edit')).classes('q-mt-md')
        ui.button('Cambia Password', on_click=lambda: ui.open('/change_password')).classes('q-mt-md')
        ui.button('Logout', on_click=lambda: ui.open('/')).classes('q-mt-md')
    else:
        ui.label("Errore nel caricamento dati notaio.")