from nicegui import ui
from app.api.api import api_session
from datetime import datetime
from typing import Optional

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
    """Formatta ISO date/ datetime in formato leggibile (DD/MM/YYYY HH:MM)"""
    if not date_str:
        return "-"
    try:
        # Supporta sia date che datetime ISO
        dt = datetime.fromisoformat(date_str)
        if dt.time().hour == 0 and dt.time().minute == 0 and dt.time().second == 0:
            return dt.strftime("%d/%m/%Y")
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        # fallback: ritorna stringa originale se parsing fallisce
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

    # helper che determina ruolo e naviga alla home corretta
    def _go_home(cid: int = cliente_id):
        user = getattr(api_session, 'user', None)
        try:
            # prova dipendente
            if user and hasattr(api_session, 'get_dipendente_id_by_user'):
                dip_id = api_session.get_dipendente_id_by_user(user.get('id'))
                if dip_id:
                    ui.navigate.to('/home_dipendente')
                    return
        except Exception:
            pass
        try:
            # prova notaio
            if user and hasattr(api_session, 'get_notaio_id_by_user'):
                notaio_id = api_session.get_notaio_id_by_user(user.get('id'))
                if notaio_id:
                    ui.navigate.to('/home_notaio')
                    return
        except Exception:
            pass
        # fallback: home cliente (passiamo cliente_id)
        ui.navigate.to(f'/home_cliente?cliente_id={cid}')

    ui.button(
        'Torna alla Home',
        icon='home',
        on_click=lambda cid=cliente_id: _go_home(cid)
    ).classes('q-pa-md q-mb-md').style(
        'background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important; color:#fff !important; border-radius:1.8em;'
    )

    # determina ruolo dell'utente (dipendente / notaio / cliente) per uso in details_url
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

        # Lista di card, una per servizio
        for servizio in servizi:
            servizio_id = servizio.get('id')
            tipo = servizio.get('tipo') or '—'
            codice = servizio.get('codiceServizio') or servizio.get('codiceCorrente') or '—'
            stato = servizio.get('statoServizio') or '—'
            data_richiesta = _format_date(servizio.get('dataRichiesta'))
            data_consegna = _format_date(servizio.get('dataConsegna'))

            # colore badge stato (logical name -> hex)
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

            with ui.card().classes('q-pa-md q-mb-md').style('border-radius:0.9em;box-shadow:0 6px 18px rgba(0,0,0,0.04);'):
                # Intestazione: tipo + codice
                with ui.row().classes('items-center').style('justify-content:space-between'):
                    with ui.row().classes('items-center'):
                        ui.label(tipo).classes('text-h6').style('margin-right:12px;font-weight:700')
                        ui.badge(codice).props('outline').classes('q-ma-xs').style('background:#e3f2fd;color:#0d47a1')
                    # stato a destra -> usa badge (compatibile con tutte le versioni NiceGUI)
                    ui.badge(stato).classes('q-ma-xs').style(f'background:{bg}; color:white; border-radius:999px; padding:.2em .6em;')

                # Meta: date e altro
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

                # Dipendente responsabile + azioni
                with ui.row().classes('items-center').style('justify-content:space-between'):
                    # dipendente responsabile
                    dip = _get_dip_responsabile(servizio_id)
                    if dip:
                        nome = (dip.get('nome') or '').strip()
                        cognome = (dip.get('cognome') or '').strip()
                        dip_label = f"{nome} {cognome}".strip() or f"ID {dip.get('id')}"
                        with ui.row().classes('items-center'):
                            ui.icon('badge', size='18px').classes('q-mr-sm')
                            ui.label('Dipendente responsabile').classes('text-caption text-grey-6 q-mr-sm')
                            ui.label(dip_label).classes('text-body2')
                    else:
                        ui.label('Dipendente responsabile: info non disponibile').classes('text-caption text-grey-6')

                    # azioni (pulsanti)
                    with ui.row().classes('items-center'):
                        ui.button('Vedi dettagli', icon='info', on_click=lambda s_id=servizio_id: ui.navigate.to(details_url(s_id))).classes('q-ml-sm').style(
                            'background: linear-gradient(90deg,#1976d2,#1565c0); color:white; border-radius:12px;'
                        )