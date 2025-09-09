from nicegui import ui

def servizi_page():
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        # Barra superiore
        with ui.row().classes('items-center q-mb-md'):
            ui.icon('account_circle', size='40px').classes('q-mr-md')
            ui.label('RICHIEDI SERVIZIO').classes('text-h5').style('background:#1a237e;color:white;border-radius:2em;padding:.5em 2em;')
            ui.input('', placeholder="Cerca...").props('dense').classes('q-ml-md').style('max-width:200px;')
        # Elenco servizi (mock: 2 servizi)
        for servizio in ['SERVIZIO 1', 'SERVIZIO 2']:
            with ui.card().classes('q-pa-md q-mb-md').style('background:#e3f2fd'):
                ui.label(servizio).classes('text-h6 q-mb-sm')
                with ui.row().classes('q-gutter-md'):
                    ui.button('Documentazione', icon='folder', on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.lower().replace(" ","_")}/documenti')).classes('q-pa-md')
                    ui.button('Carica', icon='upload', on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.lower().replace(" ","_")}/carica')).classes('q-pa-md')
                    ui.button('Scarica', icon='download', on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.lower().replace(" ","_")}/scarica')).classes('q-pa-md')