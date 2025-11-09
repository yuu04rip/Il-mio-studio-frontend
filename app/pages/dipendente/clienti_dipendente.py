from nicegui import ui
from app.api.api import api_session

def clienti_page_dipendente():
    ui.add_head_html('<link rel="stylesheet" href="/static/stylesClientiDipendente.css">')

    # === CONTENITORE CENTRALE ===
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        ui.label('Clienti').classes('text-h5 q-mt-xl q-mb-lg')
        search = ui.input('', placeholder="Cerca per nome o cognome...").props('outlined dense').classes('search-bar')
        clienti_list = ui.column().classes('full-width')

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
                    with ui.card().classes('cliente-card'):
                        ui.label(f"{cli['utente']['nome']} {cli['utente']['cognome']}").classes('cliente-nome')
                        with ui.row().classes('buttons-row'):
                            ui.button(
                                'Servizi',
                                icon='work',
                                color='primary',
                                on_click=lambda id=cli['id']: visualizza_servizi(id)
                            ).classes('cliente-btn')
                            ui.button(
                                'Documenti',
                                icon='folder',
                                color='accent',
                                on_click=lambda id=cli['id']: visualizza_documenti(id)
                            ).classes('cliente-btn green')

        def visualizza_servizi(cliente_id):
            ui.navigate.to(f'/servizi_cliente_approvati/{cliente_id}')

        def visualizza_documenti(cliente_id):
            ui.navigate.to(f'/documentazione_cliente/{cliente_id}')

        def on_search_change(e):
            refresh_clienti(search.value)

        search.on('update:model-value', on_search_change)
        refresh_clienti()
