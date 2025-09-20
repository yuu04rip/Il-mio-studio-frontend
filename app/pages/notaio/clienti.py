from nicegui import ui
from app.api.api import api_session

def clienti_page():
    ui.label('Clienti').classes('text-h5 q-mt-xl q-mb-lg').style(
        'background:#1976d2;color:white;border-radius:2em;padding:.5em 2.5em;display:block;text-align:center;font-weight:600;letter-spacing:0.04em;'
    )

    search = ui.input('', placeholder="Cerca per nome o cognome...").props('outlined dense').style('max-width:220px;margin-bottom:18px;')
    clienti_list = ui.column().classes('full-width').style('gap:18px;')

    def refresh_clienti(filter_text=""):
        clienti_list.clear()
        if filter_text:
            clienti = api_session.search_clienti(filter_text)
        else:
            resp = api_session.get('/studio/clienti/')
            clienti = resp.json() if resp.status_code == 200 else []
        if not clienti:
            with clienti_list:
                ui.label('Nessun cliente trovato.').classes('text-grey-7 q-mt-md')
        for cli in clienti:
            with clienti_list:
                with ui.card().style('background:#e3f2fd;border-radius:1em;min-height:78px;padding:1em 2em;'):
                    ui.label(f"{cli['utente']['nome']} {cli['utente']['cognome']}").classes('text-body1 q-mb-xs')
                    with ui.row().style('gap:8px;'):
                        ui.button('Servizi', icon='work', color='primary', on_click=lambda id=cli['id']: visualizza_servizi(id)).props('flat round')
                        ui.button('Documenti', icon='folder', color='accent', on_click=lambda id=cli['id']: visualizza_documenti(id)).props('flat round')
                        ui.button('Aggiungi Servizio', icon='add', color='info', on_click=lambda id=cli['id']: aggiungi_servizio(id)).props('flat round')

    def visualizza_servizi(cliente_id):
        ui.navigate.to(f'/clienti/{cliente_id}/servizi')

    def visualizza_documenti(cliente_id):
        ui.navigate.to(f'/clienti/{cliente_id}/documenti')

    def aggiungi_servizio(cliente_id):
        ui.navigate.to(f'/clienti/{cliente_id}/aggiungi_servizio')

    # RICERCA LIVE: chiama refresh_clienti ad ogni carattere!
    def on_search_change(e):
        refresh_clienti(search.value)

    search.on('update:model-value', on_search_change)
    refresh_clienti()