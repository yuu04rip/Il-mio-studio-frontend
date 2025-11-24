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

def _format_date(date_str: Optional[str], add_months: int = 0) -> str:
    """Formatta ISO date/datetime in formato leggibile (DD/MM/YYYY HH:MM)
    Aggiunge mesi se richiesto."""
    if not date_str:
        return "-"
    try:
        dt = datetime.fromisoformat(date_str)
        if add_months:
            dt += relativedelta(months=+add_months)
        if dt.time().hour == 0 and dt.time().minute == 0 and dt.time().second == 0:
            return dt.strftime("%d/%m/%Y")
        return dt.strftime("%d/%m/%Y %H:%M")
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

    ui.button(
        'Torna alla Home',
        icon='home',
        on_click=lambda cid=cliente_id: _go_home(cid)
    ).classes('q-pa-md q-mb-md').style(
        'background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important; '
        'color:#fff !important; border-radius:1.8em;'
    )

    # determina ruolo dell'utente
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
            'background:#f8fafc;border-radius:1.2em;max-width:960px;'
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

            # formattazione date
            data_richiesta = _format_date(servizio.get('dataRichiesta'))
            # Data consegna +3 mesi
            data_consegna = _format_date(servizio.get('dataConsegna'), add_months=3)

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

            # creatore del servizio
            creato_da = servizio.get('creato_da')
            op_nome = op_cognome = ''
            if isinstance(creato_da, dict):
                op_nome = (creato_da.get('nome') or '').strip()
                op_cognome = (creato_da.get('cognome') or '').strip()
            operatore_display = (op_nome + ' ' + op_cognome).strip()

            with ui.card().classes('q-pa-md q-mb-md').style(
                    'border-radius:0.9em;box-shadow:0 6px 18px rgba(0,0,0,0.04);'
            ):
                # Intestazione: tipo + codice + stato
                with ui.row().classes('items-center').style('justify-content:space-between'):
                    with ui.row().classes('items-center'):
                        ui.label(tipo).classes('text-h6').style('margin-right:12px;font-weight:700')
                        ui.badge(codice).props('outline').classes('q-ma-xs').style(
                            'background:#e3f2fd;color:#0d47a1'
                        )
                    ui.badge(stato).classes('q-ma-xs').style(
                        f'background:{bg}; color:white; border-radius:999px; padding:.2em .6em;'
                    )

                # Meta: date e codice interno
                with ui.row().classes('q-mt-sm q-mb-sm').style('gap:24px'):
                    with ui.column().style('min-width:220px'):
                        ui.label('Data richiesta').classes('text-caption text-grey-6')
                        ui.label(data_richiesta).classes('text-body2')
                    with ui.column().style('min-width:220px'):
                        ui.label('Data consegna (+3 mesi)').classes('text-caption text-grey-6')
                        ui.label(data_consegna).classes('text-body2')
                    with ui.column().style('flex:1'):
                        ui.label('Codice interno').classes('text-caption text-grey-6')
                        ui.label(servizio.get('codiceCorrente') or '-').classes('text-body2')

                # creatore + azioni
                with ui.row().classes('items-start').style('justify-content:space-between;margin-top:4px;'):
                    with ui.column():
                        if operatore_display:
                            with ui.row().classes('items-center'):
                                ui.icon('person', size='18px').classes('q-mr-xs')
                                ui.label('Creato da').classes('text-caption text-grey-6 q-mr-xs')
                                ui.label(operatore_display).classes('text-body2')
                    # azioni
                    with ui.row().classes('items-center'):
                        ui.button(
                            'Vedi dettagli',
                            icon='info',
                            on_click=lambda s_id=servizio_id: ui.navigate.to(details_url(s_id))
                        ).classes('q-ml-sm').style(
                            'background: linear-gradient(90deg,#1976d2,#1565c0); '
                            'color:white; border-radius:12px;'
                        )
