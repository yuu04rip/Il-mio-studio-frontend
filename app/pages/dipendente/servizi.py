# -*- coding: utf-8 -*-
# Aggiornato: dedup delle suggestions + visualizzazione nome cognome email come "menu a tendina"
from nicegui import ui, app
from app.api.api import api_session
from app.components.components import header
import tempfile
import os
from threading import Timer
from mimetypes import guess_type
import uuid
from typing import Dict, Optional
from starlette.responses import FileResponse, Response
from app.models.servizio import Servizio
import time

API_BASE = "http://localhost:8000"

# semplice cache client_id -> dict (contiene almeno 'nome' e 'cognome')
_CLIENT_CACHE: Dict[int, dict] = {}

TIPI_SERVIZIO = {
    'atto': 'Atto',
    'compromesso': 'Compromesso',
    'preventivo': 'Preventivo',
}

# Miglior mappatura icone
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
    """
    Recupera e memorizza in cache nome/cognome del cliente.
    Restituisce dict con almeno keys 'nome' e 'cognome' (vuote se non trovate).
    """
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
    # fallback vuoto
    info = {'nome': '', 'cognome': ''}
    _CLIENT_CACHE[cliente_id] = info
    return info


def servizi_dipendente_page():
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

    # Creiamo il dialog di creazione qui in anticipo così il button lo trova sempre
    crea_servizio_dialog = ui.dialog()

    # Configurazione ricerca
    SEARCH_MIN_LENGTH = 2  # non attivare il filtro per ricerche di 1 carattere
    DEBOUNCE_MS = 300

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        with ui.row().classes('items-center q-mb-md'):
            ui.icon('engineering', size='40px').classes('q-mr-md')
            ui.label('SERVIZI DA SVOLGERE').classes(
                'text-h5').style('background:#1a237e;color:white;border-radius:2em;padding:.5em 2em;')
            search_box = ui.input('', placeholder="Cerca servizio...").props(
                'dense').classes('q-ml-md').style('max-width:300px;')
            ui.button('Crea Servizio', icon='add',
                      on_click=lambda: crea_servizio_dialog.open()).classes('q-ml-lg q-pa-md')

        # Liste ORIGINALI - non vengono mai modificate dal filtro
        servizi_miei_originali = []
        servizi_collaborazioni_originali = []

        # Liste per il display - queste vengono filtrate
        servizi_miei_display = []
        servizi_collaborazioni_display = []

        servizi_container = ui.column().classes('full-width').style('gap:18px;')
        collaborazioni_container = ui.column().classes('full-width').style('gap:18px;')

        modifica_dialog = ui.dialog()
        with modifica_dialog:
            with ui.card().classes('q-pa-md').style('max-width:400px;'):
                ui.label('Modifica servizio').classes('text-h6 q-mb-md')
                modifica_tipo_input = ui.select(TIPI_SERVIZIO, label="Tipo servizio").props("outlined dense").classes("q-mb-sm")
                modifica_codice_corrente_input = ui.input('Codice corrente').props('outlined dense').classes('q-mb-sm')
                modifica_codice_servizio_input = ui.input('Codice servizio').props('outlined dense').classes('q-mb-sm')
                msg_modifica = ui.label().classes('text-negative q-mb-sm')
                servizio_corrente = {"id": None}

                def submit_modifica():
                    if not modifica_tipo_input.value:
                        msg_modifica.text = 'Seleziona un tipo di servizio!'
                        return

                    payload = {
                        "tipo": modifica_tipo_input.value,
                        "codiceCorrente": modifica_codice_corrente_input.value,
                        "codiceServizio": modifica_codice_servizio_input.value,
                    }
                    try:
                        api_session.patch(f'/studio/servizi/{servizio_corrente["id"]}', payload)
                        ui.notify('Servizio modificato!', color='positive')
                        modifica_dialog.close()
                        carica_tutti_servizi()
                    except Exception as e:
                        msg_modifica.text = f'Errore: {e}'

                ui.button('Salva', on_click=submit_modifica).classes('q-mt-md q-pa-md')
                ui.button('Annulla', on_click=lambda: modifica_dialog.close()).classes('q-ml-md q-pa-md')

        def apri_modifica(servizio):
            servizio_corrente["id"] = servizio.id
            modifica_tipo_input.value = servizio.tipo
            modifica_codice_corrente_input.value = servizio.codiceCorrente
            modifica_codice_servizio_input.value = servizio.codiceServizio
            msg_modifica.text = ''
            modifica_dialog.open()

        def carica_tutti_servizi():
            """
            Carica i servizi dal backend nelle liste ORIGINALI
            Qui raccogliamo SOLO i servizi assegnati al dipendente (i "miei")
            e le eventuali collaborazioni/altre assegnazioni separatamente.
            Non includiamo servizi approvati in queste liste.
            """
            nonlocal servizi_miei_originali, servizi_collaborazioni_originali
            servizi_miei_originali = []
            servizi_collaborazioni_originali = []

            try:
                res_creati = api_session.visualizza_lavoro_da_svolgere(dipendente_id) or []
                res_in_lavorazione = api_session.visualizza_servizi_inizializzati(dipendente_id) or []
                res_completati = api_session.visualizza_servizi_completati(dipendente_id) or []
                res_altri = api_session.get_altri_servizi(dipendente_id) or []

                combined = []
                for r in [res_creati, res_in_lavorazione, res_completati]:
                    if isinstance(r, list):
                        combined.extend(r)

                def is_visible_servizio(s):
                    stato = str(s.get('statoServizio', '')).upper()
                    return stato != 'APPROVATO'

                servizi_miei_originali = [Servizio.from_dict(s) for s in combined if is_visible_servizio(s)]
                servizi_collaborazioni_originali = [Servizio.from_dict(s) for s in res_altri if is_visible_servizio(s)]

                all_servizi = servizi_miei_originali + servizi_collaborazioni_originali
                cliente_ids = {s.cliente_id for s in all_servizi if getattr(s, 'cliente_id', None)}
                for cid in cliente_ids:
                    _get_cliente_min_info(cid)

                mostra_tutti_servizi()
            except Exception as e:
                print(f"Errore caricamento servizi: {e}")

        def mostra_tutti_servizi():
            servizi_miei_display[:] = servizi_miei_originali[:]
            servizi_collaborazioni_display[:] = servizi_collaborazioni_originali[:]
            refresh_servizi()
            refresh_servizi_altri()

        def elimina_servizio(servizio_id):
            try:
                api_session.elimina_servizio(servizio_id)
                ui.notify("Servizio eliminato!", color="positive")
                servizi_miei_originali[:] = [s for s in servizi_miei_originali if s.id != servizio_id]
                servizi_collaborazioni_originali[:] = [s for s in servizi_collaborazioni_originali if s.id != servizio_id]
                mostra_tutti_servizi()
            except Exception as e:
                ui.notify(f"Errore eliminazione: {e}", color="negative")

        def inoltra_servizio_notaio(servizio_id):
            try:
                api_session.inoltra_servizio_notaio(servizio_id)
                ui.notify("Servizio inoltrato al notaio!", color="positive")
                carica_tutti_servizi()
            except Exception as e:
                ui.notify(str(e), color="negative")

        def inizializza_servizio(servizio_id):
            try:
                api_session.inizializza_servizio(servizio_id)
                ui.notify("Servizio inizializzato!", color="positive")
                carica_tutti_servizi()
            except Exception as e:
                ui.notify(str(e), color="negative")

        def refresh_servizi():
            servizi_container.clear()
            if not servizi_miei_display:
                with servizi_container:
                    ui.label('Nessun servizio assegnato presente.').classes(
                        "text-grey-7 q-mt-md").style("text-align:center;font-size:1.12em;")
                return

            for servizio in servizi_miei_display:
                with ui.card().classes('q-pa-md q-mb-md').style('background:#e0f7fa;'):
                    stato = str(servizio.statoServizio).lower()
                    if stato == 'approvato':
                        card_style = 'background:#e8f5e8;'
                    elif stato == 'rifiutato':
                        card_style = 'background:#ffebee;'
                    elif stato == 'consegnato':
                        card_style = 'background:#f3e5f5;'

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
                    with ui.row().classes('items-center q-gutter-xs'):
                        ui.icon(get_icon_for_stato(str(servizio.statoServizio).upper()), size='24px').classes('q-mr-xs')
                        ui.label(f"Stato: {servizio.statoServizio}").classes('text-subtitle2 q-mb-xs')
                    with ui.row().classes('q-gutter-md'):
                        if stato == 'creato':
                            ui.button('Inizializza', icon='play_arrow', on_click=lambda s=servizio: inizializza_servizio(s.id)).classes('q-pa-md')
                        if stato == 'in_lavorazione':
                            ui.button('Inoltra al notaio', icon='send', on_click=lambda s=servizio: inoltra_servizio_notaio(s.id)).classes('q-pa-md')
                            ui.button('Modifica', icon='edit', on_click=lambda s=servizio: apri_modifica(s)).classes('q-pa-md')
                            ui.button('Elimina', icon='delete', on_click=lambda s=servizio: elimina_servizio(s.id)).classes('q-pa-md')
                        if stato in ['approvato', 'rifiutato', 'consegnato']:
                            ui.button('Visualizza dettagli', icon='visibility', on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/dettagli'))
                        ui.button('Documentazione', icon='folder', on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti')).classes('q-pa-md')

        def refresh_servizi_altri():
            collaborazioni_container.clear()
            if not servizi_collaborazioni_display:
                with collaborazioni_container:
                    ui.label('Nessuna collaborazione trovata.').classes(
                        "text-grey-7 q-mt-md").style("text-align:center;font-size:1.12em;")
                return

            for servizio in servizi_collaborazioni_display:
                with collaborazioni_container:
                    nome = getattr(servizio, 'clienteNome', None) or getattr(servizio, 'cliente_nome', None)
                    cognome = getattr(servizio, 'clienteCognome', None) or getattr(servizio, 'cliente_cognome', None)
                    if not nome and not cognome:
                        cliente_info = _get_cliente_min_info(getattr(servizio, 'cliente_id', None))
                        nome = cliente_info.get('nome', '')
                        cognome = cliente_info.get('cognome', '')
                    titolo_base = servizio.tipo or ''
                    titolo_cliente = f" di {nome} {cognome}".strip() if (nome or cognome) else ''
                    ui.label(f"{titolo_base}{titolo_cliente} (Codice: {servizio.codiceServizio})").classes('text-h6 q-mb-sm')
                    ui.button('Documentazione', icon='folder', on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti')).classes('q-pa-md')

        def filtra_servizi(testo_ricerca):
            testo = testo_ricerca.strip().lower()
            if not testo or len(testo) < SEARCH_MIN_LENGTH:
                mostra_tutti_servizi()
                return
            tokens = [t for t in testo.split() if t]
            def match(servizio):
                nome = getattr(servizio, 'clienteNome', None) or getattr(servizio, 'cliente_nome', None) or ''
                cognome = getattr(servizio, 'clienteCognome', None) or getattr(servizio, 'cliente_cognome', None) or ''
                cliente_full = f"{nome} {cognome}".strip()
                fields = ' '.join([
                    str(servizio.tipo or ''),
                    str(servizio.codiceServizio or ''),
                    str(servizio.codiceCorrente or ''),
                    cliente_full,
                ]).lower()
                words = fields.split()
                for token in tokens:
                    if not any(w.startswith(token) for w in words):
                        return False
                return True
            servizi_miei_display[:] = [s for s in servizi_miei_originali if match(s)]
            servizi_collaborazioni_display[:] = [s for s in servizi_collaborazioni_originali if match(s)]
            refresh_servizi()
            refresh_servizi_altri()

        carica_tutti_servizi()

    # Definizione del dialog di creazione (popola il dialog precedentemente creato)
    with crea_servizio_dialog:
        with ui.card().classes('q-pa-md').style('max-width:400px;'):
            ui.label('Crea nuovo servizio').classes('text-h6 q-mb-md')

            # Autocomplete / ricerca cliente
            cliente_search_input = ui.input('Cerca cliente (nome o cognome)').props('outlined dense').classes('q-mb-sm')
            # variabile Python per memorizzare l'id selezionato (evita hidden input)
            cliente_id_sel = {'id': None}
            cliente_selected_label = ui.label('').classes('q-mb-sm')
            suggestions_container = ui.column().classes('q-mb-sm')

            # helper per debounce (semplice)
            last_input_ts = {'t': 0}
            # flag per sopprimere la ricerca quando impostiamo programmaticamente il valore
            suppress_search = {'v': False}

            def show_suggestions(results):
                """
                Mostra la lista di risultati come menu a tendina con nome cognome email e bottone seleziona.
                Rimuove duplicati per id e fornisce fallback leggibile.
                """
                suggestions_container.clear()
                # rendi il contenitore visibile e con scroll
                suggestions_container.style('background:#ffffff;border:1px solid #e0e0e0;border-radius:6px;max-height:220px;overflow:auto;padding:6px;')
                seen = set()
                if not results:
                    with suggestions_container:
                        ui.label('Nessun risultato').classes('text-grey-6 q-pa-sm')
                    return
                for c in results:
                    cid = c.get('id')
                    if cid in seen:
                        continue
                    seen.add(cid)
                    nome = (c.get('nome') or '').strip()
                    cognome = (c.get('cognome') or '').strip()
                    email = (c.get('email') or '').strip()

                    # fallback display text
                    display_name = f"{nome} {cognome}".strip()
                    if not display_name:
                        display_name = email or f"id {cid}"

                    # callback per selezionare il cliente e inserire i dati nell'input
                    def pick_client(_cid=cid, _nome=nome, _cognome=cognome, _email=email, _display=display_name):
                        try:
                            # Log debug
                            print(f"[DEBUG] pick_client start -> id={_cid} display={_display}")
                            # imposta l'id selezionato nella var Python
                            cliente_id_sel['id'] = int(_cid)
                            # sopprimi temporaneamente la ricerca
                            suppress_search['v'] = True
                            # imposta visibile nel campo di ricerca il testo selezionato e aggiornalo
                            cliente_search_input.value = _display
                            cliente_search_input.update()
                            # label di conferma e notifica
                            cliente_selected_label.text = f"Selezionato: {_nome} {_cognome} (id {_cid})" if (_nome or _cognome) else f"Selezionato: {_email} (id {_cid})"
                            ui.notify(f"Cliente selezionato: {_display}", color="positive")
                            print(f"[DEBUG] pick_client -> id={_cid} saved in cliente_id_sel")
                        except Exception as ex:
                            # evita che l'eccezione faccia crashare il server -> la pagina non verrà ricaricata
                            print(f"[DEBUG] Errore in pick_client: {ex}")
                            ui.notify("Errore interno durante la selezione cliente", color="negative")
                        finally:
                            # puliamo suggerimenti e riattiviamo la ricerca
                            suggestions_container.clear()
                            suppress_search['v'] = False

                    # MODIFICA CRITICA: Aggiungi type="button" per prevenire il comportamento di submit
                    with suggestions_container:
                        with ui.row().classes('items-center q-pa-sm').style('gap:12px;border-bottom:1px solid #f0f0f0;'):
                            ui.label(display_name).classes('text-body1')
                            if email:
                                ui.label(email).classes('text-grey-6').style('margin-left:8px')
                            # MODIFICA: Aggiungi explicitamente type="button" per prevenire il refresh della pagina
                            ui.button('Seleziona', on_click=lambda _=None, _p=pick_client: _p()).props('flat type="button"').classes('q-ml-auto')

            def on_cliente_search(e=None):
                # Ignora aggiornamenti quando stiamo impostando programmaticamente il valore
                if suppress_search.get('v'):
                    return
                q = cliente_search_input.value or ''
                q = str(q).strip()
                if len(q) < 2:
                    suggestions_container.clear()
                    return
                # semplice debounce logic (aggiorna timestamp)
                now = int(time.time() * 1000)
                last_input_ts['t'] = now
                try:
                    results = api_session.search_clienti(q) or []
                    print(f"[DEBUG] search_clienti('{q}') -> {len(results)} risultati")
                    show_suggestions(results)
                except Exception as exc:
                    # intercettiamo eccezioni per evitare crash lato server
                    print(f"[DEBUG] Errore search_clienti: {exc}")
                    suggestions_container.clear()

            cliente_search_input.on('update:model-value', on_cliente_search)

            tipo_input = ui.select(TIPI_SERVIZIO, label="Tipo servizio").props("outlined dense").classes("q-mb-sm")
            codice_corrente_input = ui.input('Codice corrente').props('outlined dense').classes('q-mb-sm')
            msg_crea = ui.label().classes('text-negative q-mb-sm')
            # dipendente_id catturato dal contesto
            try:
                user = api_session.user
                dipendente_id = api_session.get_dipendente_id_by_user(user['id']) if user else None
            except Exception:
                dipendente_id = None

            def submit_servizio():
                if not cliente_id_sel.get('id'):
                    msg_crea.text = 'Seleziona un cliente dalla lista (usa la ricerca)!'
                    return
                if not tipo_input.value:
                    msg_crea.text = 'Seleziona un tipo di servizio!'
                    return
                try:
                    codice_val = int(codice_corrente_input.value)
                except Exception:
                    msg_crea.text = 'Codice corrente deve essere un numero intero'
                    return
                try:
                    res = api_session.crea_servizio(
                        int(cliente_id_sel.get('id')),
                        tipo_input.value,
                        codice_val,
                        dipendente_id=dipendente_id
                    )
                    codice_generato = None
                    try:
                        if isinstance(res, dict):
                            codice_generato = res.get('codiceServizio') or res.get('codice_servizio')
                    except Exception:
                        codice_generato = None

                    if codice_generato:
                        ui.notify(f'Servizio creato! Codice: {codice_generato}', color='positive')
                    else:
                        ui.notify('Servizio creato!', color='positive')

                    # clear form
                    cliente_search_input.value = ''
                    cliente_search_input.update()
                    cliente_id_sel['id'] = None
                    cliente_selected_label.text = ''
                    suggestions_container.clear()
                    tipo_input.value = None
                    codice_corrente_input.value = ''
                    crea_servizio_dialog.close()
                    carica_tutti_servizi()
                except Exception as e:
                    msg_crea.text = f'Errore: {e}'

            ui.button('Crea', on_click=submit_servizio).classes('q-mt-md q-pa-md')
            ui.button('Annulla', on_click=lambda: crea_servizio_dialog.close()).classes('q-ml-md q-pa-md')

    # Pulsante flottante sempre visibile (utile se vuoi un accesso rapido alla creazione)
    ui.button('Crea Servizio', icon='add', on_click=lambda: crea_servizio_dialog.open()).props('flat').classes('fixed bottom-6 right-6 q-pa-md bg-primary text-white')

# eventuale registrazione della pagina nell'app se usi router
try:
    # se usi un router o un sistema di registrazione, registra qui
    pass
except Exception:
    pass