from nicegui import ui
from app.api.api import api_session
from app.components.components import header

def servizi_cliente_page():
    header("Servizi")
    res = api_session.get('/servizi')
    if res.status_code == 200:
        servizi = res.json()
        for servizio in servizi:
            with ui.card().classes('q-mb-md'):
                ui.label(f"Servizio: {servizio['tipo']}")
                ui.label(f"Codice Servizio: {servizio['codiceServizio']}")
                ui.label(f"Stato: {'Attivo' if servizio['statoServizio'] else 'Inattivo'}")
                ui.button('Dettagli', on_click=lambda s=servizio: ui.open(f'/servizi/{s["id"]}'))
    else:
        ui.label("Nessun servizio trovato.")
    ui.button('Richiedi nuovo servizio', on_click=richiedi_servizio).classes('q-mt-lg')

def dettaglio_servizio_page(servizio_id):
    header("Dettaglio Servizio")
    res = api_session.get(f'/servizi/{servizio_id}')
    if res.status_code == 200:
        servizio = res.json()
        ui.label(f"Tipo servizio: {servizio['tipo']}")
        ui.label(f"Codice Servizio: {servizio['codiceServizio']}")
        ui.label(f"Data richiesta: {servizio['dataRichiesta']}")
        ui.label(f"Data consegna: {servizio['dataConsegna']}")
        ui.label(f"Stato: {'Attivo' if servizio['statoServizio'] else 'Inattivo'}")
        # Documentazione associata
        lavoro_caricato = servizio.get('lavoroCaricato', [])
        ui.label(f"Documentazione associata:")
        for doc in lavoro_caricato:
            with ui.row():
                ui.label(doc['filename'])
                ui.button('Scarica', icon='download', on_click=lambda d=doc: download_documento(d['id']))
        # Eventuali azioni aggiuntive
        if not servizio['statoServizio']:
            ui.button('Accetta servizio', on_click=lambda: accetta_servizio(servizio['id'])).classes('q-mt-md')
    else:
        ui.label("Servizio non trovato.")
    ui.button('Torna ai servizi', on_click=lambda: ui.open('/servizi')).classes('q-mt-lg')

def richiedi_servizio():
    ui.notify("Funzionalità richiesta servizio non implementata")

def download_documento(doc_id):
    ui.notify(f"Scarica documento {doc_id}")

def accetta_servizio(servizio_id):
    res = api_session.post(f"/servizi/{servizio_id}/accetta", {})
    if res.status_code == 200:
        ui.notify("Servizio accettato!")
        ui.open('/servizi')
    else:
        ui.notify("Errore accettazione servizio.")