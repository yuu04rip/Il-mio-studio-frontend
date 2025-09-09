from nicegui import ui

def home_cliente():
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        ui.label('HOME').classes('text-h5 q-mb-lg').style('background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;')
        with ui.row().classes('q-gutter-lg q-mb-md'):
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')).classes('q-pa-xl').style('min-width:160px;')
            ui.button('DOCUMENTAZIONE', icon='folder', on_click=lambda: ui.navigate.to('/documentazione')).classes('q-pa-xl').style('min-width:160px;')
        with ui.row().classes('q-gutter-lg'):
            ui.button('EFFETTUA PAGAMENTO', icon='payments', on_click=lambda: ui.navigate.to('/pagamento')).classes('q-pa-xl').style('min-width:160px;')
            ui.button('SERVIZI', icon='add', on_click=lambda: ui.navigate.to('/servizi')).classes('q-pa-xl').style('min-width:160px;')

def home_dipendente():
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        ui.label('HOME').classes('text-h5 q-mb-lg').style('background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;')
        with ui.row().classes('q-gutter-lg'):
            ui.button('CLIENTI', icon='groups', on_click=lambda: ui.navigate.to('/clienti')).classes('q-pa-xl').style('min-width:160px;')
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')).classes('q-pa-xl').style('min-width:160px;')

def home_notaio():
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        ui.label('HOME').classes('text-h5 q-mb-lg').style('background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;')
        with ui.row().classes('q-gutter-lg q-mb-md'):
            ui.button('CLIENTI', icon='groups', on_click=lambda: ui.navigate.to('/clienti')).classes('q-pa-xl').style('min-width:160px;')
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')).classes('q-pa-xl').style('min-width:160px;')
        with ui.row().classes('q-gutter-lg'):
            ui.button('DIPENDENTI', icon='add', on_click=lambda: ui.navigate.to('/dipendenti')).classes('q-pa-xl').style('min-width:160px;')
            ui.button('ACCETTAZIONE', icon='check', on_click=lambda: ui.navigate.to('/accettazione')).classes('q-pa-xl').style('min-width:160px;')