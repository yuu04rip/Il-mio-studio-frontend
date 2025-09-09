from nicegui import ui
from app.api.api import api_session
from app.components.components import header

def add_dipendente_page():
    header("Aggiungi Dipendente")
    nome = ui.input('Nome')
    cognome = ui.input('Cognome')
    email = ui.input('Email')
    numero = ui.input('Numero telefonico')
    password = ui.input('Password', password=True)
    ruolo = ui.select(['DIPENDENTE', 'ASSISTENTE', 'CONTABILE'], label='Ruolo')
    msg = ui.label()
    def do_add():
        data = {
            'nome': nome.value,
            'cognome': cognome.value,
            'email': email.value,
            'numeroTelefonico': int(numero.value),
            'password': password.value,
            'ruolo': ruolo.value,
        }
        resp = api_session.post('/dipendenti/aggiungi', data)
        if resp.status_code == 200:
            msg.text = "Dipendente aggiunto!"
        else:
            msg.text = resp.json().get('detail','Errore aggiunta dipendente')
    ui.button('Aggiungi', on_click=do_add).classes('q-mt-lg')
    ui.button('Torna', on_click=lambda: ui.open('/home_notaio')).classes('q-mt-md')