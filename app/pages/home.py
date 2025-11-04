from nicegui import ui
from app.pages.cliente.chatbox import chatbox

def home_cliente(cliente_id: int):
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        ui.label('HOME').classes('text-h5 q-mb-lg').style(
            'background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;'
        )
        with ui.row().classes('q-gutter-lg q-mb-md'):
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')).classes('q-pa-xl').style('min-width:160px;')
            ui.button('DOCUMENTAZIONE', icon='folder', on_click=lambda: ui.navigate.to('/documentazione')).classes('q-pa-xl').style('min-width:160px;')
        with ui.row().classes('q-gutter-lg'):
            ui.button('EFFETTUA PAGAMENTO', icon='payments', on_click=lambda: ui.navigate.to('/pagamento')).classes('q-pa-xl').style('min-width:160px;')
            ui.button('SERVIZI', icon='work',
                      on_click=lambda: ui.navigate.to(f'/servizi_cliente/{cliente_id}')
                      ).classes('q-pa-xl').style('min-width:160px;')

    chatbox(cliente_id)

def home_dipendente():
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        ui.label('HOME').classes('text-h5 q-mb-lg') \
            .style('background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;')
        with ui.row().classes('q-gutter-lg q-mb-md'):
            ui.button('CLIENTI', icon='groups', on_click=lambda: ui.navigate.to('/clienti_dipendente')) \
                .classes('q-pa-xl').style('min-width:160px;')
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')) \
                .classes('q-pa-xl').style('min-width:160px;')
        with ui.row().classes('q-gutter-lg'):
            ui.button('SERVIZI DA SVOLGERE', icon='work', on_click=lambda: ui.navigate.to('/servizi')) \
                .classes('q-pa-xl').style('min-width:160px;')

def home_notaio():
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto shadow-5') \
            .style('max-width:550px;background:#fafdff;'):
        ui.icon('account_circle').style('font-size:3em;color:#1976d2;margin-bottom:12px;')
        ui.label('HOME').classes('text-h5 q-mb-lg').style(
            'background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;letter-spacing:0.04em;font-weight:700;font-size:1.32em;margin-bottom:28px;'
        )
        with ui.row().classes('q-gutter-lg q-mb-md').style('justify-content:center;'):
            ui.button('CLIENTI', icon='groups', on_click=lambda: ui.navigate.to('/clienti')) \
                .classes('q-pa-xl').style('min-width:160px;font-weight:600;font-size:1.08em;')
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')) \
                .classes('q-pa-xl').style('min-width:160px;font-weight:600;font-size:1.08em;')
        with ui.row().classes('q-gutter-lg').style('justify-content:center;'):
            ui.button('DIPENDENTI', icon='add', on_click=lambda: ui.navigate.to('/dipendenti')) \
                .classes('q-pa-xl').style('min-width:160px;font-weight:600;font-size:1.08em;')
            ui.button('ACCETTAZIONE', icon='check', on_click=lambda: ui.navigate.to('/accettazione')) \
                .classes('q-pa-xl').style('min-width:160px;font-weight:600;font-size:1.08em;')