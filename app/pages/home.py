from nicegui import ui
from app.api.api import api_session
from .chatbox import chatbox  # importa la chat

def home_cliente(cliente_id: int):

    ui.add_head_html("""
    <style>
    /* 🧱 CARD PRINCIPALE (contenitore centrale) */
    .q-card {
        background: rgb(240, 240, 240) !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0) !important;
        padding: 48px !important;
        width: 80% !important;
        max-width: 1000px !important;
        min-height: 600px !important;
        margin: 60px auto !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.4s ease-in-out !important;
    }

    /* 🔹 Stato normale (chat chiusa) */
    .q-card.default {
        transform: translateY(0);
    }

    /* 🔹 Stato con chat aperta */
    .q-card.chat-open {
        width: 90% !important;
        max-width: 1200px !important;
        min-height: 800px !important;
        transform: translateY(-50px);
    }

    /* 🔹 Sposta più in alto l’etichetta HOME */
    .q-card.chat-open .text-h5 {
        transform: translateY(-60px);
        transition: transform 0.4s ease;
    }

    /* 🔹 Pulsanti si abbassano leggermente */
    .q-card.chat-open .q-row:nth-of-type(2),
    .q-card.chat-open .q-row:nth-of-type(3) {
        transform: translateY(20px);
        transition: transform 0.4s ease;
    }
    </style>
    """)

    # 🧱 Contenitore principale
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto default'):
        ui.label('HOME').classes('text-h5 q-mb-lg')

        with ui.row().classes('q-gutter-md q-mb-lg'):
            ui.button('Servizi', on_click=lambda: ui.notify('Azione Servizi'))
            ui.button('Documenti', on_click=lambda: ui.notify('Azione Documenti'))

        with ui.row().classes('q-gutter-md'):
            ui.button('Pagamenti', on_click=lambda: ui.notify('Azione Pagamenti'))
            ui.button('Profilo', on_click=lambda: ui.notify('Azione Profilo'))

    # 💬 Aggiungi la chatbox
    chatbox(cliente_id)


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
            

