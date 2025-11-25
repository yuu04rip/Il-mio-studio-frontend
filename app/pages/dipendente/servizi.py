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
    ui.add_head_html("""
<style>
.custom-label {
    font-weight: 600;
    font-size: 2rem; /* aumentato da 1.2rem a 2rem */
    color: #1976d2;
    letter-spacing: 0.5px;
    margin: 0;
    padding: 0;
    background: none;
    box-shadow: none;
}
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
    width: auto !important;
    max-width: 300px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    letter-spacing: 0.5px !important;
}
.custom-button-blue-light-panels {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 2.5em !important;
    padding: 0.8em 1.2em !important;
    font-size: 1.2rem !important;
    width: 100% !important;
    max-width: 300px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    letter-spacing: 0.5px !important;
}
</style>
    """)
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
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto').style('width: 900px;background: rgba(240,240,240) !important;box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important;border-radius: 2.5em !important;border: 1.7px solid #e3eaf1 !important;backdrop-filter: blur(6px);align-items: center;'):
        with ui.row().classes('items-center q-mb-md').style('align-items: center; gap: 40px;justify-content: space-between;'):
            ui.icon('archive', size='40px').classes('q-mr-md').style('color:#1976d2')
            ui.label('SERVIZI ARCHIVIATI').classes(
                'custom-label')

        # Liste ORIGINALI - i servizi archiviati restituiti dall'API
        servizi_originali = []
        servizi_display = []

        servizi_container = ui.column().classes('full-width').style('gap:18px;').style('align-items: center;')

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
                    with ui.card().classes('q-pa-md q-mb-md').style('background:#e0f7fa;border-radius:1em;min-height:72px;padding:1em 2em;width:100%;'):
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
                                'dettagli',
                                icon='visibility',
                                color='primary',
                                on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/dettagli')
                            ).props('flat round type="button"')

                            ui.button(
                                'Documentazione',
                                icon='folder',
                                color='accent',
                                on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti')
                            ).props('flat round type="button"')

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
                                color='secondary',
                                on_click=lambda sid=servizio.id: dearchivia_and_refresh(sid)
                            ).props('flat round type="button"')
        # caricamento iniziale della lista archiviati
        carica_tutti_servizi_archiviati()

    # registrazione della pagina se necessario
    try:
        pass
    except Exception:
        pass