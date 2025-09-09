from nicegui import ui
from app.api.api import api_session
from app.components.components import header

def profile_page():
    header("Profilo Utente")
    user = api_session.user or {}
    with ui.card().classes('q-pa-xl q-mx-auto'):
        ui.label(f"Nome: {user.get('nome','')}")
        ui.label(f"Cognome: {user.get('cognome','')}")
        ui.label(f"Email: {user.get('email','')}")
        ui.label(f"Telefono: {user.get('numeroTelefonico','')}")
        ui.label(f"Ruolo: {user.get('ruolo','')}")
        ui.button('Modifica Dati Anagrafici', on_click=lambda: ui.open('/profilo/edit')).classes('q-mt-md')
        ui.button('Cambia Email', on_click=lambda: ui.open('/profilo/edit')).classes('q-mt-md')
        ui.button('Modifica Password', on_click=lambda: ui.open('/change_password')).classes('q-mt-md')
        ui.button('Logout', on_click=lambda: ui.open('/')).classes('q-mt-md')

def edit_profile_page():
    header("Modifica Profilo")
    user = api_session.user or {}
    nome = ui.input('Nome', value=user.get('nome',''))
    cognome = ui.input('Cognome', value=user.get('cognome',''))
    email = ui.input('Email', value=user.get('email',''))
    telefono = ui.input('Telefono', value=str(user.get('numeroTelefonico','')))
    msg = ui.label()
    def do_update():
        data = {
            'nome': nome.value,
            'cognome': cognome.value,
            'email': email.value,
            'numeroTelefonico': int(telefono.value) if telefono.value else None
        }
        resp = api_session.put('/users/me/update', data)
        if resp.status_code == 200:
            api_session.set_user(resp.json())
            msg.text = "Profilo aggiornato!"
        else:
            msg.text = resp.json().get('detail','Errore aggiornamento profilo')
    ui.button('Salva', on_click=do_update).classes('q-mt-md')
    ui.button('Torna al profilo', on_click=lambda: ui.open('/profilo')).props('flat').classes('q-mt-md')