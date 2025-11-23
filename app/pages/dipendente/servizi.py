from nicegui import ui
from app.api.api import api_session
from app.components.components import header
import time
from typing import Dict, Optional
from app.models.servizio import Servizio

API_BASE = "http://localhost:8000"

# semplice cache client_id -> dict (contiene almeno 'nome' e 'cognome')
_CLIENT_CACHE: Dict[int, dict] = {}

TIPI_SERVIZIO = {
    'atto': 'Atto',
    'compromesso': 'Compromesso',
    'preventivo': 'Preventivo',
}


def get_icon_for_stato(stato):
    icons = {
        'CREATO': 'pending_actions',
        'IN_LAVORAZIONE': 'play_circle',
        'IN_ATTESA_APPROVAZIONE': 'hourglass_empty',
        'APPROVATO': 'check_circle',
        'RIFIUTATO': 'cancel',
        'CONSEGNATO': 'done_all',
    }
    return icons.get(stato, 'help')


def _get_cliente_min_info(cliente_id: Optional[int]) -> dict:
    if not cliente_id:
        return {'nome': '', 'cognome': ''}
    if cliente_id in _CLIENT_CACHE:
        return _CLIENT_CACHE[cliente_id]
    try:
        resp = api_session.get(f'/studio/clienti/{cliente_id}')
        if resp.status_code == 200:
            data = resp.json()
            info = {
                'nome': data.get('nome', '') or '',
                'cognome': data.get('cognome', '') or '',
            }
            _CLIENT_CACHE[cliente_id] = info
            return info
    except Exception:
        pass
    info = {'nome': '', 'cognome': ''}
    _CLIENT_CACHE[cliente_id] = info
    return info


def servizi_dipendente_page():
    """
    Pagina dipendente: mostra SOLO servizi archiviati.
    Azioni disponibili:
      - Visualizza dettagli
      - Documentazione
      - Dearchivia (ripristina il servizio tra quelli attivi)
    """
    user = api_session.user
    dipendente_id = None
    if user:
        try:
            dipendente_id = api_session.get_dipendente_id_by_user(user['id'])
        except Exception as e:
            ui.notify(
                f"Impossibile trovare il dipendente tecnico per questo utente ({user['id']}): {e}",
                color="negative"
            )
            ui.label("Errore: dipendente tecnico non trovato.").classes('text-negative q-mt-xl')
            return

    if not dipendente_id:
        ui.label("Utente non autenticato o non dipendente tecnico").classes('text-negative q-mt-xl')
        return

    # Titolo pagina (archiviati)
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        with ui.row().classes('items-center q-mb-md'):
            ui.icon('archive', size='40px').classes('q-mr-md')
            ui.label('SERVIZI ARCHIVIATI').classes(
                'text-h5').style('background:#263238;color:white;border-radius:2em;padding:.5em 2em;')

        # Liste ORIGINALI - i servizi archiviati restituiti dall'API
        servizi_originali = []
        servizi_display = []

        servizi_container = ui.column().classes('full-width').style('gap:18px;')

        def carica_tutti_servizi_archiviati():
            """
            Carica tutti i servizi archiviati dal backend usando api_session.mostra_servizi_archiviati()
            e popola servizi_originali / servizi_display, poi chiama mostra_servizi().
            """
            nonlocal servizi_originali, servizi_display
            servizi_originali = []
            servizi_display = []
            try:
                res = api_session.mostra_servizi_archiviati() or []
                # res dovrebbe essere una lista di dict compatibili con Servizio.from_dict
                servizi_originali = [Servizio.from_dict(s) for s in res]
                servizi_display = servizi_originali[:]
                cliente_ids = {s.cliente_id for s in servizi_originali if getattr(s, 'cliente_id', None)}
                for cid in cliente_ids:
                    _get_cliente_min_info(cid)
                mostra_servizi()
            except Exception as e:
                print(f"Errore caricamento servizi archiviati: {e}")
                ui.notify(f"Errore caricamento servizi archiviati: {e}", color="negative")

        def mostra_servizi():
            refresh_servizi()

        def refresh_servizi():
            """
            Ricostruisce il contenuto del container servizi_container
            a partire da servizi_display.
            """
            servizi_container.clear()
            if not servizi_display:
                with servizi_container:
                    ui.label('Nessun servizio archiviato.').classes(
                        "text-grey-7 q-mt-md").style("text-align:center;font-size:1.12em;")
                return

            for servizio in servizi_display:
                with servizi_container:
                    with ui.card().classes('q-pa-md q-mb-md').style('background:#f5f5f5;'):
                        stato = str(servizio.statoServizio).upper()
                        nome = getattr(servizio, 'clienteNome', None) or getattr(servizio, 'cliente_nome', None)
                        cognome = getattr(servizio, 'clienteCognome', None) or getattr(servizio, 'cliente_cognome', None)
                        if not nome and not cognome:
                            cliente_info = _get_cliente_min_info(getattr(servizio, 'cliente_id', None))
                            nome = cliente_info.get('nome', '')
                            cognome = cliente_info.get('cognome', '')

                        titolo_base = servizio.tipo or ''
                        titolo_cliente = f" di {nome} {cognome}".strip() if (nome or cognome) else ''
                        titolo = f"{titolo_base}{titolo_cliente} (Codice: {servizio.codiceServizio})"

                        ui.label(titolo).classes('text-h6 q-mb-sm')

                        with ui.row().classes('items-center q-gutter-xs q-mb-sm'):
                            ui.icon(get_icon_for_stato(stato), size='24px').classes('q-mr-xs')
                            ui.label(f"Stato: {servizio.statoServizio}").classes('text-subtitle2 q-mb-xs')

                        # Azioni: sola lettura + dearchiviazione
                        with ui.row().classes('q-gutter-md'):
                            ui.button(
                                'Visualizza dettagli',
                                icon='visibility',
                                on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/dettagli')
                            ).classes('q-pa-md')

                            ui.button(
                                'Documentazione',
                                icon='folder',
                                on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti')
                            ).classes('q-pa-md')

                            # Bottone Dearchivia per riportare il servizio nello stato attivo
                            def dearchivia_and_refresh(sid=servizio.id):
                                try:
                                    api_session.dearchivia_servizio(sid)
                                    ui.notify("Servizio dearchiviato!", color="positive")
                                except Exception as e:
                                    ui.notify(f"Errore dearchiviazione: {e}", color="negative")
                                finally:
                                    # ricarica la lista degli archiviati — aggiorna il contenuto senza reload completo
                                    carica_tutti_servizi_archiviati()

                            ui.button(
                                'Dearchivia',
                                icon='unarchive',
                                on_click=lambda sid=servizio.id: dearchivia_and_refresh(sid)
                            ).classes('q-pa-md')

        # caricamento iniziale della lista archiviati
        carica_tutti_servizi_archiviati()

    # registrazione della pagina se necessario
    try:
        pass
    except Exception:
        pass