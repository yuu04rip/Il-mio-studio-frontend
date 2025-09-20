from nicegui import ui
from app.api.api import api_session

def dipendenti_page():
    ui.label('Gestione Dipendenti').classes('text-h5 q-mt-xl q-mb-lg').style(
        'background:#1976d2;color:white;border-radius:2em;padding:.5em 2.5em;display:block;text-align:center;font-weight:600;letter-spacing:0.04em;'
    )

    # Sezione aggiunta dipendente
    with ui.card().classes('q-mb-xl shadow-3').style('max-width:440px;margin:auto;'):
        ui.label('Aggiungi Dipendente').classes('text-h6 q-mb-md')
        nome = ui.input('Nome').props('outlined dense')
        cognome = ui.input('Cognome').props('outlined dense')
        email = ui.input('Email').props('outlined dense type=email')
        numero = ui.input('Numero telefonico').props('outlined dense type=tel')
        password = ui.input('Password', password=True).props('outlined dense')
        # Se vuoi solo dipendenti puoi togliere la select, oppure lasciare per futura espansione
        ruolo = ui.select(
            options=['DIPENDENTE', 'NOTAIO'], label='Ruolo'
        ).props('outlined dense')
        msg = ui.label().classes('text-negative q-mt-sm')

        def do_add():
            msg.text = ""
            data = {
                'nome': nome.value,
                'cognome': cognome.value,
                'email': email.value,
                'numeroTelefonico': numero.value,
                'password': password.value,
            }
            if not all([data['nome'], data['cognome'], data['email'], data['password']]):
                msg.text = "Compila tutti i campi obbligatori."
                return
            try:
                if ruolo.value == "DIPENDENTE":
                    resp = api_session.register_dipendente(data)
                    ui.notify('Dipendente aggiunto!', color='positive')
                    refresh_dipendenti()
                elif ruolo.value == "NOTAIO":
                    msg.text = "Registrazione notai non supportata qui. Usa la sezione dedicata."
                else:
                    msg.text = "Ruolo non valido."
            except Exception as e:
                msg.text = f"Errore: {str(e)}"

        ui.button('Aggiungi', on_click=do_add).classes('q-mt-md')

    # Sezione lista dipendenti
    with ui.card().classes('shadow-5').style('max-width:600px;margin:auto;'):
        ui.label('Lista Dipendenti').classes('text-h6 q-mb-md')
        dip_list = ui.column().classes('full-width').style('gap:14px;')

        def refresh_dipendenti():
            dip_list.clear()
            resp = api_session.get('/studio/dipendenti/')
            if resp.status_code == 200:
                for dip in resp.json():
                    with dip_list:
                        with ui.row().style('align-items:center;gap:18px;'):
                            ui.label(f"{dip['utente']['nome']} {dip['utente']['cognome']} ({dip['utente']['ruolo'].capitalize()})").classes('text-body1')
                            ui.button('Elimina', icon='delete', color='negative', on_click=lambda id=dip['id']: elimina_dipendente(id)).props('flat round')

        def elimina_dipendente(dipendente_id):
            try:
                resp = api_session.delete(f"/studio/dipendente/{dipendente_id}/distruggi")
                if resp.status_code == 200:
                    ui.notify('Dipendente eliminato!', color='positive')
                else:
                    ui.notify('Errore eliminazione', color='negative')
            except Exception:
                ui.notify('Errore di connessione', color='negative')
            refresh_dipendenti()

        refresh_dipendenti()