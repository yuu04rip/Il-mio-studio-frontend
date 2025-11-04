from nicegui import ui
from app.api.api import api_session

def documentazione_servizio_page_cliente(servizio_id: int):
    """Visualizza la documentazione associata al servizio (solo quella del servizio)"""
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto').style('max-width: 800px;'):
        ui.label('Documentazione del Servizio').classes('text-h5 q-mb-xl')
        doc_list = ui.column().classes('full-width').style('gap:20px;')

        resp = api_session.get(f'/documentazione/servizi/{servizio_id}/documenti')
        if resp.status_code == 200:
            docs = resp.json()
            if docs:
                for doc in docs:
                    with doc_list:
                        with ui.card().style('background:#f4f7fb;border-radius:1.5em;min-height:72px;padding:1em 2em;margin-bottom:8px;'):
                            ui.label(doc.get('filename', 'Documento')).classes('text-body1 text-blue-grey-8')
                            ui.button(
                                'Scarica',
                                icon='download',
                                on_click=lambda d=doc: download_documento_servizio(d['id'])
                            ).classes('q-mt-sm')
            else:
                with doc_list:
                    ui.label('Nessun documento associato a questo servizio.').classes('text-grey-7 q-mt-md')
        else:
            with doc_list:
                ui.label('Errore nel recupero dei documenti').classes('text-negative')

def download_documento_servizio(doc_id):
    url = f"http://localhost:8000/documentazione/download/{doc_id}"
    ui.run_javascript(f"window.open('{url}', '_blank')")