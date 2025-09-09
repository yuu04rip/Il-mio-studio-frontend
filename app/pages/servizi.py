from nicegui import ui
from app.api.api import api_session
from app.models.servizio import Servizio

def servizi_page():
    user = api_session.user
    cliente_id = user.get('id') if user else None
    if not cliente_id:
        ui.label("Utente non autenticato").classes('text-negative q-mt-xl')
        return

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        # Barra superiore
        with ui.row().classes('items-center q-mb-md'):
            ui.icon('account_circle', size='40px').classes('q-mr-md')
            ui.label('SERVIZI RICHIESTI').classes('text-h5').style('background:#1a237e;color:white;border-radius:2em;padding:.5em 2em;')
            search_box = ui.input('', placeholder="Cerca servizio...").props('dense').classes('q-ml-md').style('max-width:200px;')

        servizi = []
        # Chiamata API per recuperare servizi dell'utente autenticato
        res = api_session.get(f'/servizi?cliente_id={cliente_id}')
        if res.status_code == 200:
            servizi = [Servizio.from_dict(s) for s in res.json()]
        else:
            ui.label("Errore nel recupero dei servizi.").classes("text-negative q-mt-lg")

        servizi_container = ui.column().classes('full-width').style('gap:18px;')

        def refresh_servizi(filter_text=""):
            servizi_container.clear()
            filtered = servizi
            if filter_text:
                filtered = [s for s in servizi if filter_text.lower() in s.tipo.lower() or filter_text.lower() in s.codiceServizio.lower()]
            if not filtered:
                with servizi_container:
                    ui.label('Nessun servizio trovato.').classes("text-grey-7 q-mt-md").style("text-align:center;font-size:1.12em;")
            for servizio in filtered:
                if getattr(servizio, "is_deleted", False):
                    continue
                with servizi_container:
                    with ui.card().classes('q-pa-md q-mb-md').style('background:#e3f2fd'):
                        ui.label(f"{servizio.tipo}").classes('text-h6 q-mb-sm')
                        with ui.row().classes('q-gutter-md'):
                            ui.button(
                                'Documentazione', icon='folder',
                                on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti')
                            ).classes('q-pa-md')
                            ui.button(
                                'Carica', icon='upload',
                                on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/carica')
                            ).classes('q-pa-md')
                            ui.button(
                                'Scarica', icon='download',
                                on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/scarica')
                            ).classes('q-pa-md')

        # Trigger ricerca
        def on_search_change(e):
            refresh_servizi(search_box.value)

        search_box.on('update:model-value', on_search_change)

        refresh_servizi()
