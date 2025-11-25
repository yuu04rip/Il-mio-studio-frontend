from nicegui import ui
from app.api.api import api_session
from datetime import datetime
from typing import Optional
from dateutil.relativedelta import relativedelta



# cache servizio_id -> dipendente dict (min info)
_DIP_CACHE: dict = {}

def _get_dip_responsabile(servizio_id: int):
    if not servizio_id:
        return None
    if servizio_id in _DIP_CACHE:
        return _DIP_CACHE[servizio_id]
    try:
        resp = api_session.get(f'/studio/servizi/{servizio_id}/dipendenti')
        if getattr(resp, 'status_code', None) == 200:
            dip_list = resp.json()
            if dip_list:
                dip = dip_list[0]
                info = {
                    'id': dip.get('id'),
                    'nome': dip.get('nome', '') or '',
                    'cognome': dip.get('cognome', '') or '',
                }
                _DIP_CACHE[servizio_id] = info
                return info
    except Exception:
        pass
    _DIP_CACHE[servizio_id] = None
    return None

def _format_date(date_str: Optional[str]) -> str:
    """Formatta ISO date/datetime in formato leggibile (DD/MM/YYYY HH:MM) e aggiunge 3 mesi"""
    if not date_str:
        return "-"
    try:
        dt = datetime.fromisoformat(date_str)
        dt_plus3 = dt + relativedelta(months=+3)  # aggiunta 3 mesi
        if dt_plus3.time().hour == 0 and dt_plus3.time().minute == 0 and dt_plus3.time().second == 0:
            return dt_plus3.strftime("%d/%m/%Y")
        return dt_plus3.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(date_str)

# mapping logical color names to hex codes for badges
_COLOR_MAP = {
    'positive': '#43a047',  # green
    'negative': '#e53935',  # red
    'secondary': '#6d4c41', # brown/secondary
    'info': '#1976d2',      # blue
}

def servizi_cliente_approvati_page(cliente_id: int):
    ui.add_head_html("""
<style>

.custom-button-blue-light {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 2.5em !important;
    padding: 0.8em 1.2em !important;
    font-size: 1.2rem !important;
    width: 300px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    letter-spacing: 0.5px !important;
    heigth:20 px;
}
</style>
    """)
    """Pagina per visualizzare tutti i servizi APPROVATI di un cliente (UI più curata)"""

    def _go_home(cid: int = cliente_id):
        
        user = getattr(api_session, 'user', None)
        try:
            if user and hasattr(api_session, 'get_dipendente_id_by_user'):
                dip_id = api_session.get_dipendente_id_by_user(user.get('id'))
                if dip_id:
                    ui.navigate.to('/home_dipendente')
                    return
        except Exception:
            pass
        try:
            if user and hasattr(api_session, 'get_notaio_id_by_user'):
                notaio_id = api_session.get_notaio_id_by_user(user.get('id'))
                if notaio_id:
                    ui.navigate.to('/home_notaio')
                    return
        except Exception:
            pass
        ui.navigate.to(f'/home_cliente?cliente_id={cid}')


    # determina ruolo dell'utente (dipendente / notaio / cliente) per usare la giusta pagina dettagli
    user = getattr(api_session, 'user', None)
    user_role = 'cliente'
    try:
        if user and hasattr(api_session, 'get_dipendente_id_by_user'):
            dip_id = api_session.get_dipendente_id_by_user(user.get('id'))
            if dip_id:
                user_role = 'dipendente'
    except Exception:
        pass
    try:
        if user and hasattr(api_session, 'get_notaio_id_by_user'):
            notaio_id = api_session.get_notaio_id_by_user(user.get('id'))
            if notaio_id:
                user_role = 'notaio'
    except Exception:
        pass

    def details_url(servizio_id: int) -> str:
        if user_role == 'dipendente':
            return f'/servizi/{servizio_id}/dettagli'
        elif user_role == 'notaio':
            return f'/servizi_notaio/{servizio_id}/dettagli'
        else:
            return f'/servizi_cliente/{cliente_id}/dettagli/{servizio_id}'

    # Card principale
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto').style(
            'background: rgba(240,240,240); border-radius:2.5em;'
    ):
        ui.label('SERVIZI APPROVATI').classes('text-h5').style(
            'color:#1565c0;text-align:center;font-weight:700;margin-bottom:10px;'
        )

        try:
            servizi_resp = api_session.get(f'/studio/clienti/{cliente_id}/servizi_approvati')
            servizi_resp.raise_for_status()
            servizi = servizi_resp.json()
        except Exception as e:
            ui.notify(f"Errore nel caricamento: {e}", color="negative")
            ui.label("Impossibile caricare i servizi approvati").classes('text-negative q-mt-md')
            return

        if not servizi:
            ui.label("Nessun servizio approvato trovato.").classes('text-grey-7 q-mt-md')
            return

        for servizio in servizi:
            servizio_id = servizio.get('id')
            tipo = servizio.get('tipo') or '—'
            codice = servizio.get('codiceServizio') or servizio.get('codiceCorrente') or '—'
            stato = servizio.get('statoServizio') or '—'
            data_richiesta = _format_date(servizio.get('dataRichiesta'))
            data_consegna = _format_date(servizio.get('dataConsegna'))

            # colore badge stato
            stato_lower = str(stato).lower()
            if 'approv' in stato_lower:
                stato_color = 'positive'
            elif 'rifiut' in stato_lower:
                stato_color = 'negative'
            elif 'consegn' in stato_lower:
                stato_color = 'secondary'
            else:
                stato_color = 'info'
            bg = _COLOR_MAP.get(stato_color, _COLOR_MAP['info'])

            # creatore del servizio (come avevamo fatto per i servizi archiviati)
            creato_da = servizio.get('creato_da')
            op_nome = op_cognome = ''
            if isinstance(creato_da, dict):
                op_nome = (creato_da.get('nome') or '').strip()
                op_cognome = (creato_da.get('cognome') or '').strip()
            operatore_display = (op_nome + ' ' + op_cognome).strip()

            with ui.card().classes('q-pa-md q-mb-md').style(
                    'background:#e3f2fd;border-radius:1em;min-height:72px;padding:1em 2em;width:100%;'
            ):
                # Intestazione: tipo + codice + stato
                with ui.row().classes('items-center').style('justify-content:space-between'):
                    with ui.row().classes('items-center'):
                        ui.label(tipo).classes('text-h6').style('margin-right:12px;font-weight:700')
                        ui.label(codice).classes('text-h6').style('margin-right:12px;font-weight:700')
                        ui.label(stato).classes('text-h6').style('margin-right:12px;font-weight:700')
                        
                # Meta: date e codice interno
                with ui.row().classes('q-mt-sm q-mb-sm').style('gap:24px'):
                    with ui.column().style('min-width:220px'):
                        ui.label('Data richiesta').classes('text-caption text-grey-6')
                        ui.label(data_richiesta).classes('text-body2')
                    with ui.column().style('min-width:220px'):
                        ui.label('Data consegna').classes('text-caption text-grey-6')
                        ui.label(data_consegna).classes('text-body2')
                    with ui.column().style('flex:1'):
                        ui.label('Codice interno').classes('text-caption text-grey-6')
                        ui.label(servizio.get('codiceCorrente') or '-').classes('text-body2')

                # creatore + dipendente responsabile + azioni
                with ui.row().classes('items-start').style('justify-content:space-between;margin-top:4px;'):
                    with ui.column():
                        # creatore del servizio (notaio/dipendente che l'ha creato)
                        if operatore_display:
                            with ui.row().classes('items-center'):
                                ui.icon('person', size='18px').classes('q-mr-xs')
                                ui.label('Creato da').classes('text-caption text-grey-6 q-mr-xs')
                                ui.label(operatore_display).classes('text-body2')
                    # azioni (pulsanti)
                    with ui.card().classes('q-pa-md q-mb-md').style(
                        'width:400px; max-width:90%; '
                        'background: transparent !important; '
                        'border: none !important; '
                        'box-shadow: none !important;'
                    ):
                        with ui.row().style('width:100%; justify-content: flex-end;'):
                            ui.button(
                                'Vedi dettagli',
                                icon='info',
                                on_click=lambda s_id=servizio_id: ui.navigate.to(details_url(s_id))
                            ).classes('custom-button-blue-light ')