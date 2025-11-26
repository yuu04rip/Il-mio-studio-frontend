from nicegui import ui

from app.api.api import api_session
from app.pages.cliente.chatbox import chatbox

def home_cliente(cliente_id: int = None):
    """
    Home cliente. Se il caller non passa cliente_id (ma solo user logged),
    la funzione prova a risolverlo chiamando /studio/clienti/by_user/{user_id}.
    """
    ui.add_head_html('<link rel="stylesheet" href="/static/stylesHome.css">')

    def _resolve_and_open_servizi():
        # se abbiamo già cliente_id passato, usalo subito
        cid = cliente_id
        if cid:
            ui.navigate.to(f'/servizi_cliente/{cid}')
            return

        # altrimenti prova a risolvere dal user loggato (api_session.user)
        user = getattr(api_session, 'user', None) or {}
        uid = user.get('id')
        if not uid:
            ui.notify('Impossibile risolvere il cliente: login richiesto.', color='negative')
            return

        try:
            resp = api_session.get(f'/studio/clienti/by_user/{uid}')
            if getattr(resp, 'status_code', None) == 200:
                body = resp.json()
                cid = body.get('id') if isinstance(body, dict) else body
                if cid:
                    ui.navigate.to(f'/servizi_cliente/{cid}')
                    return
            # not found or non-200
            ui.notify('Cliente non trovato per l\'utente corrente.', color='negative')
        except Exception as e:
            ui.notify(f'Errore risoluzione cliente: {e}', color='negative')

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        ui.label('HOME').classes('text-h5 q-mb-lg').style(
            'background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;'
        )
        with ui.row().classes('q-gutter-lg q-mb-md'):
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')) \
                .classes('q-pa-xl').style('min-width:160px;')
            ui.button('DOCUMENTAZIONE', icon='folder', on_click=lambda: ui.navigate.to('/documentazione')) \
                .classes('q-pa-xl').style('min-width:160px;')
        with ui.row().classes('q-gutter-lg'):
            ui.button('EFFETTUA PAGAMENTO', icon='payments', on_click=lambda: ui.navigate.to('/pagamento')) \
                .classes('q-pa-xl').style('min-width:160px;')
            # usa handler che risolve cliente_id se necessario
            ui.button('SERVIZI', icon='work', on_click=_resolve_and_open_servizi) \
                .classes('q-pa-xl').style('min-width:160px;')

    # se hai già cliente_id, passa al chatbox; in alternativa chatbox può risolvere internamente
    chatbox(cliente_id)


def home_dipendente():
    ui.add_head_html('<link rel="stylesheet" href="/static/stylesHome.css">')
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        ui.label('HOME').classes('text-h5 q-mb-lg') \
            .style('background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;')
        with ui.row().classes('q-gutter-lg q-mb-md'):
            ui.button('CLIENTI', icon='groups', on_click=lambda: ui.navigate.to('/clienti_dipendente')) \
                .classes('q-pa-xl').style('min-width:160px;')
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')) \
                .classes('q-pa-xl').style('min-width:160px;')
        with ui.row().classes('q-gutter-lg'):
            ui.button('SERVIZI ARCHIVIATI', icon='work', on_click=lambda: ui.navigate.to('/servizi')) \
                .classes('q-pa-xl').style('min-width:160px;')


def home_notaio():
    ui.add_head_html('<link rel="stylesheet" href="/static/stylesHome.css">')
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto shadow-5') \
            .style('max-width:550px;background:#fafdff;'):
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
            ui.button('ARCHIVIAZIONE', icon='folder', on_click=lambda: ui.navigate.to('/servizi_notaio_archiviati')) \
                .classes('q-pa-xl').style('min-width:160px;font-weight:600;font-size:1.08em;')