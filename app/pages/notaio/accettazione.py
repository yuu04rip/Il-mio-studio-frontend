from nicegui import ui
from app.api.api import api_session

def accettazione_page():
    ui.label('ACCETTAZIONE').classes(
        'text-h5 q-mt-xl q-mb-lg'
    ).style('background:#1976d2;color:white;border-radius:2em;padding:.5em 2.5em;display:block;text-align:center;font-weight:600;letter-spacing:0.04em;')

    servizi_list = ui.column().classes('full-width').style('gap:18px;')

    def refresh_servizi():
        servizi_list.clear()
        user = api_session.user
        if not user:
            ui.notify("Utente non autenticato", color="negative")
            return

        # Recupera tutti i servizi da approvare (stato IN_ATTESA_APPROVAZIONE)
        try:
            resp = api_session.get('/studio/notai/servizi')  # Usa l'API corretta!
        except Exception:
            ui.notify("Errore connessione backend", color="negative")
            return

        if resp.status_code == 200:
            servizi = resp.json()
            if not servizi:
                with servizi_list:
                    ui.label('Nessun servizio da approvare.').classes('text-grey-7 q-mt-md')
            for servizio in servizi:
                # Mostra solo quelli con stato IN_ATTESA_APPROVAZIONE
                if servizio.get('statoServizio', '').lower() == 'in_attesa_approvazione':
                    with servizi_list:
                        with ui.card().style('background:#e3f2fd;border-radius:1em;min-height:78px;padding:1em 2em;'):
                            ui.label(
                                f"{servizio['tipo']} - {servizio['codiceServizio']} | Stato: {servizio.get('statoServizio','')}"
                            ).classes('text-body1 q-mb-xs')
                            with ui.row().style('gap:8px;'):
                                ui.button('Accetta', icon='check', color='positive',
                                          on_click=lambda id=servizio['id']: accetta_servizio(id)).props('flat round')
                                ui.button('Rifiuta', icon='close', color='negative',
                                          on_click=lambda id=servizio['id']: rifiuta_servizio(id)).props('flat round')
                                ui.button('Documenti', icon='folder', color='accent',
                                          on_click=lambda id=servizio['id']: visualizza_documenti(id)).props('flat round')
        else:
            ui.notify("Errore nel recupero dei servizi.", color="negative")

    def accetta_servizio(servizio_id):
        try:
            # Accetta: chiama l'API di approvazione (cambia stato a APPROVATO)
            resp = api_session.post(f'/studio/servizi/{servizio_id}/approva')
            if resp.status_code == 200:
                ui.notify('Servizio accettato!', color='positive')
            else:
                ui.notify('Errore accettazione servizio', color='negative')
        except Exception:
            ui.notify('Errore connessione', color='negative')
        refresh_servizi()

    def rifiuta_servizio(servizio_id):
        try:
            # Rifiuta: chiama l'API di rifiuto (cambia stato a RIFIUTATO)
            resp = api_session.post(f'/studio/servizi/{servizio_id}/rifiuta')
            if resp.status_code == 200:
                ui.notify('Servizio rifiutato!', color='positive')
            else:
                ui.notify('Errore rifiuto servizio', color='negative')
        except Exception:
            ui.notify('Errore connessione', color='negative')
        refresh_servizi()

    def visualizza_documenti(servizio_id):
        ui.navigate.to(f'/servizi/{servizio_id}/documenti')

    refresh_servizi()