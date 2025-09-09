from nicegui import ui
from app.api.api import api_session
from app.components.components import header

def clienti_lista_page():
    header("Elenco Clienti")
    res = api_session.get('/clienti')
    if res.status_code == 200:
        clienti = res.json()
        for cliente in clienti:
            with ui.card().classes('q-mb-md'):
                ui.label(f"{cliente['nome']} {cliente['cognome']}")
                ui.button('Dettagli', on_click=lambda c=cliente: ui.open(f'/clienti/{c["id"]}'))
    else:
        ui.label("Nessun cliente trovato.")

def dettaglio_cliente_page(cliente_id):
    header("Dettaglio Cliente")
    res = api_session.get(f'/clienti/{cliente_id}')
    if res.status_code == 200:
        cliente = res.json()
        ui.label(f"Nome: {cliente['nome']}")
        ui.label(f"Cognome: {cliente['cognome']}")
        ui.label(f"Email: {cliente['email']}")
        ui.label(f"Servizi richiesti:")
        for servizio in cliente.get('servizi', []):
            with ui.card().classes('q-mb-md'):
                ui.label(f"Servizio: {servizio['tipo']}")
                ui.button('Gestisci documentazione', on_click=lambda s=servizio: gestisci_doc_servizio(cliente_id, s['id']))
    else:
        ui.label("Cliente non trovato.")
    ui.button('Torna ai clienti', on_click=lambda: ui.open('/clienti')).classes('q-mt-lg')

def gestisci_doc_servizio(cliente_id, servizio_id):
    # Placeholder per gestione documenti di servizio per cliente
    ui.notify(f"Gestione documentazione servizio {servizio_id} per cliente {cliente_id}")