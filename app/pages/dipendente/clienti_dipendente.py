from nicegui import ui
from app.api.api import api_session
from app.models.servizio import Servizio
from typing import Dict, Optional
import time

SEARCH_MIN_LENGTH = 2  # soglia minima per attivare il filtro

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
    return icons.get(str(stato).upper(), 'help')


def clienti_page_dipendente():
    ui.label('Clienti').classes('text-h5 q-mt-xl q-mb-lg').style(
        'background:#1976d2;color:white;border-radius:2em;padding:.5em 2.5em;'
        'display:block;text-align:center;font-weight:600;letter-spacing:0.04em;'
    )

    # mostra il nome del dipendente (se disponibile in api_session.user)
    user = getattr(api_session, 'user', None) or {}
    user_nome = user.get('nome') or user.get('username') or ''
    user_cognome = user.get('cognome') or ''
    if user_nome or user_cognome:
        ui.label(f'Operatore: {user_nome} {user_cognome}').classes('text-subtitle2 q-mb-sm')

    # tenta di recuperare dipendente_id (utile per la creazione del servizio e per mostrare azioni)
    try:
        dipendente_id = api_session.get_dipendente_id_by_user(user['id']) if user and user.get('id') else None
        print('[DEBUG] dipendente_id risolto:', dipendente_id)
    except Exception as e:
        dipendente_id = None
        print('[DEBUG] errore get_dipendente_id_by_user:', e)
        ui.notify(f"Impossibile recuperare il dipendente tecnico per l'utente corrente: {e}", color='negative')

    # dialog globale di creazione servizio (riutilizzabile per ogni cliente)
    crea_servizio_dialog = ui.dialog()
    crea_msg = None
    selected_cliente = {'id': None, 'display': ''}

    # definiamo i widget del dialog fuori così possiamo aggiornarli da open_crea_dialog_for_cliente
    with crea_servizio_dialog:
        with ui.card().classes('q-pa-md').style('max-width:420px;'):
            ui.label('Crea nuovo servizio').classes('text-h6 q-mb-md')
            cliente_label = ui.label('').classes('q-mb-sm')
            tipo_input = ui.select(TIPI_SERVIZIO, label="Tipo servizio").props("outlined dense").classes("q-mb-sm")
            codice_corrente_input = ui.input('Codice corrente (opzionale)').props('outlined dense').classes('q-mb-sm')
            crea_msg = ui.label().classes('text-negative q-mb-sm')

            def submit_crea():
                print('[DEBUG] submit_crea chiamato, selected_cliente:', selected_cliente, 'tipo:', tipo_input.value)
                # validazioni minime
                if not selected_cliente.get('id'):
                    crea_msg.text = 'Cliente non selezionato'
                    return
                if not tipo_input.value:
                    crea_msg.text = 'Seleziona un tipo di servizio!'
                    return

                # se non abbiamo dipendente_id, non possiamo impostare il creatore
                if dipendente_id is None:
                    crea_msg.text = 'Dipendente non riconosciuto: impossibile impostare il creatore del servizio.'
                    ui.notify('Dipendente non riconosciuto, effettua di nuovo il login.', color='negative')
                    print('[DEBUG] submit_crea: dipendente_id è None, blocco creazione')
                    return

                codice_raw = (codice_corrente_input.value or '').strip()
                try:
                    codice_val = int(codice_raw) if codice_raw != '' else None
                except Exception:
                    crea_msg.text = 'Codice corrente deve essere un numero intero'
                    return

                try:
                    cliente_for_nav = int(selected_cliente['id'])
                    print('[DEBUG] chiamata api_session.crea_servizio con:',
                          'cliente_id=', cliente_for_nav,
                          'tipo=', tipo_input.value,
                          'codice_corrente=', codice_val,
                          'dipendente_id=', dipendente_id)

                    # chiamata API: passiamo esplicitamente anche dipendente_id
                    res = api_session.crea_servizio(
                        cliente_for_nav,
                        tipo_input.value,
                        codice_corrente=codice_val,
                        dipendente_id=dipendente_id,
                    )

                    # debug / log risposta
                    try:
                        print('crea_servizio response (raw):', repr(res))
                        if hasattr(res, 'json'):
                            print('crea_servizio response JSON:', res.json())
                    except Exception as e:
                        print('crea_servizio: risposta non-json / tipo:', type(res), 'errore:', e)

                    # estraiamo eventuale oggetto creato e id per mostrare subito il servizio
                    created_obj = None
                    created_id = None
                    try:
                        if isinstance(res, dict):
                            created_obj = res
                        elif hasattr(res, 'json'):
                            created_obj = res.json()
                        if created_obj:
                            created_id = created_obj.get('id')
                        print('[DEBUG] created_id:', created_id, 'created_obj:', created_obj)
                    except Exception as e:
                        print('[DEBUG] errore parse risposta crea_servizio:', e)
                        created_obj = None
                        created_id = None

                    # estraiamo eventuale codice generato per notifica
                    codice_generato = None
                    try:
                        if created_obj:
                            codice_generato = created_obj.get('codiceServizio') or created_obj.get('codice_servizio')
                    except Exception as e:
                        print('[DEBUG] errore estrazione codice_generato:', e)
                        codice_generato = None

                    if codice_generato:
                        ui.notify(f'Servizio creato! Codice: {codice_generato}', color='positive')
                    else:
                        ui.notify('Servizio creato!', color='positive')

                    # pulizia campi
                    tipo_input.value = None
                    codice_corrente_input.value = ''
                    cliente_display = selected_cliente.get('display', f'id {cliente_for_nav}')
                    selected_cliente['id'] = None
                    selected_cliente['display'] = ''
                    cliente_label.text = ''

                    crea_servizio_dialog.close()
                    # apriamo la vista dei servizi inline per quel cliente e passiamo created info
                    print('[DEBUG] apro mostra_servizi_cliente_dialog per cliente_id=', cliente_for_nav)
                    mostra_servizi_cliente_dialog(
                        cliente_for_nav,
                        cliente_display,
                        created_id=created_id,
                        created_obj=created_obj,
                    )
                except Exception as e:
                    crea_msg.text = f'Errore: {e}'
                    ui.notify(f'Errore creazione servizio: {e}', color='negative')
                    print('[DEBUG] eccezione in submit_crea:', e)

            with ui.row().classes('q-mt-md'):
                ui.button('Crea', on_click=submit_crea).classes('q-pa-md')
                ui.button('Annulla', on_click=lambda: crea_servizio_dialog.close()).classes('q-ml-md q-pa-md')

    # barra di ricerca + checkbox "solo i miei"
    row = ui.row().classes('items-center q-mb-md').style('gap:12px;')
    with row:
        search = ui.input('', placeholder="Cerca per nome o cognome...").props('outlined dense').style(
            'max-width:320px;margin-bottom:0;'
        )
        only_mine = ui.checkbox('Solo i miei', value=True).props('dense')
        ui.button('Aggiorna', icon='refresh', on_click=lambda: carica_clienti()).props('flat')

    # area risultati
    clienti_list = ui.column().classes('full-width').style('gap:18px;')

    # dati in memoria
    clienti_originali = []   # tutti i clienti (se richiesti)
    miei_clienti_ids = set() # ids dei clienti assegnati al dipendente

    # -------------------------
    # Funzioni per la gestione dei servizi
    # -------------------------
    def archivia_servizio_ui(servizio_id: int, carica_callback=None):
        try:
            api_session.archivia_servizio(servizio_id)
            ui.notify("Servizio archiviato!", color="positive")
            if carica_callback:
                carica_callback()
        except Exception as e:
            ui.notify(f"Errore archiviazione: {e}", color="negative")
            print('[DEBUG] errore archivia_servizio_ui:', e)

    def inizializza_servizio_ui(servizio_id: int, carica_callback=None):
        try:
            api_session.inizializza_servizio(servizio_id)
            ui.notify("Servizio inizializzato!", color="positive")
            if carica_callback:
                carica_callback()
        except Exception as e:
            ui.notify(f"Errore inizializzazione: {e}", color="negative")
            print('[DEBUG] errore inizializza_servizio_ui:', e)

    def inoltra_al_notaio_ui(servizio_id: int, carica_callback=None):
        try:
            api_session.inoltra_servizio_notaio(servizio_id)
            ui.notify("Servizio inoltrato al notaio!", color="positive")
            if carica_callback:
                carica_callback()
        except Exception as e:
            ui.notify(f"Errore inoltro: {e}", color="negative")
            print('[DEBUG] errore inoltra_al_notaio_ui:', e)

    def elimina_servizio_ui(servizio_id: int, carica_callback=None):
        try:
            api_session.elimina_servizio(servizio_id)
            ui.notify("Servizio eliminato!", color="positive")
            if carica_callback:
                carica_callback()
        except Exception as e:
            ui.notify(f"Errore eliminazione: {e}", color="negative")
            print('[DEBUG] errore elimina_servizio_ui:', e)

    # -------------------------
    # Dialog inline: mostra e gestisci servizi per un cliente
    # -------------------------
    def mostra_servizi_cliente_dialog(cliente_id: int, cliente_display: str, created_id=None, created_obj=None):
        print('[DEBUG] mostra_servizi_cliente_dialog aperto per cliente_id=', cliente_id)
        dialog = ui.dialog()
        servizi_originali = []
        servizi_display = []
        servizi_container = None

        with dialog:
            with ui.card().classes('q-pa-xl').style('max-width:1000px;'):
                ui.label(f'Servizi per {cliente_display} (id {cliente_id})').classes('text-h6 q-mb-md')
                ricerca_servizi = ui.input('', placeholder="Cerca servizio (tipo / codice)...").props(
                    'outlined dense'
                ).style('max-width:420px;')
                with ui.row().classes('q-mb-md'):
                    ui.button('Aggiorna', icon='refresh', on_click=lambda: carica_servizi_cliente()).props('flat')

                servizi_container = ui.column().classes('full-width').style('gap:12px;')

                def carica_servizi_cliente():
                    nonlocal servizi_originali, servizi_display
                    servizi_originali = []
                    servizi_display = []
                    try:
                        print('[DEBUG] chiamata GET /studio/servizi?cliente_id=', cliente_id)
                        resp = api_session.get(f'/studio/servizi?cliente_id={cliente_id}')
                        print('[DEBUG] status servizi cliente:', resp.status_code)
                        if resp.status_code == 200:
                            arr = resp.json()
                            print('[DEBUG] risposta servizi cliente:', arr)
                            print('[DEBUG] numero servizi totali per cliente:', len(arr))
                            filtered = [
                                s for s in arr
                                if not s.get('archived', False) and not s.get('is_deleted', False)
                            ]
                            print('[DEBUG] numero servizi non archiviati:', len(filtered))
                            servizi_originali = [Servizio.from_dict(s) for s in filtered]
                        else:
                            servizi_originali = []
                            print('[DEBUG] risposta non 200 servizi cliente:', resp.text)
                    except Exception as e:
                        print(f"[DEBUG] Errore caricamento servizi cliente {cliente_id}: {e}")
                        servizi_originali = []

                    # Se abbiamo il servizio creato ma non è ancora presente nella GET, inseriamolo in testa
                    try:
                        if created_id and not any(
                                getattr(s, 'id', None) == created_id
                                for s in servizi_originali
                        ):
                            print('[DEBUG] created_id non trovato in servizi_originali, provo ad inserire in testa')
                            if created_obj:
                                try:
                                    servizi_originali.insert(0, Servizio.from_dict(created_obj))
                                except Exception as e:
                                    print('[DEBUG] errore insert created_obj:', e)
                                    ui.notify(
                                        'Servizio creato ma non completamente convertibile per la visualizzazione immediata.',
                                        color='warning',
                                    )
                            else:
                                ui.notify(
                                    'Servizio creato ma non ancora visibile; premi Aggiorna se non compare.',
                                    color='warning',
                                )
                    except Exception as e:
                        print('[DEBUG] errore gestione created_id in carica_servizi_cliente:', e)

                    servizi_display = servizi_originali[:]
                    print('[DEBUG] servizi_display pronto con', len(servizi_display), 'servizi')
                    refresh_ui()

                def refresh_ui():
                    print('[DEBUG] refresh_ui: rendering', len(servizi_display), 'servizi; dipendente_id=', dipendente_id)
                    servizi_container.clear()
                    if not servizi_display:
                        with servizi_container:
                            ui.label('Nessun servizio trovato per questo cliente.').classes('text-grey-7')
                        return

                    for servizio in servizi_display:
                        # normalizza tipo
                        titolo_tipo = (
                            servizio.tipo.value if hasattr(servizio.tipo, 'value')
                            else (servizio.tipo or '')
                        )
                        codice_visualizzato = servizio.codiceServizio or servizio.codiceCorrente or 'N/A'
                        titolo = f"{titolo_tipo} (Codice: {codice_visualizzato})"

                        # normalizza stato a stringa maiuscola
                        if hasattr(servizio.statoServizio, 'value'):
                            stato_str = str(servizio.statoServizio.value).upper()
                        else:
                            stato_str = (
                                str(servizio.statoServizio).upper()
                                if servizio.statoServizio is not None else 'N/A'
                            )

                        print(
                            '[DEBUG] servizio id=', getattr(servizio, 'id', None),
                            'statoServizio raw=', servizio.statoServizio,
                            'stato_str=', stato_str
                        )

                        with servizi_container:
                            with ui.card().classes('q-pa-md q-mb-sm').style('background:#f8f9fa;'):
                                ui.label(titolo).classes('text-h6 q-mb-sm')
                                with ui.row().classes('items-center q-gutter-xs'):
                                    ui.icon(get_icon_for_stato(stato_str), size='24px').classes('q-mr-xs')
                                    ui.label(f"Stato: {stato_str}").classes('text-subtitle2 q-mb-xs')

                                with ui.row().classes('q-gutter-md q-mt-sm'):
                                    ui.button(
                                        'Documentazione',
                                        icon='folder',
                                        on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti'),
                                    ).classes('q-pa-sm')
                                    ui.button(
                                        'Dettagli',
                                        icon='visibility',
                                        on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/dettagli'),
                                    ).classes('q-pa-sm')
                                    ui.button(
                                        'Archivia',
                                        icon='archive',
                                        on_click=lambda sid=servizio.id: archivia_servizio_ui(
                                            sid, carica_servizi_cliente
                                        ),
                                    ).classes('q-pa-sm')

                                    is_dipendente = dipendente_id is not None
                                    stato_servizio = stato_str

                                    print(
                                        '[DEBUG] is_dipendente=', is_dipendente,
                                        'stato_servizio per branch pulsanti=', stato_servizio
                                    )

                                    if is_dipendente:
                                        if stato_servizio == 'CREATO':
                                            ui.button(
                                                'Inizializza',
                                                icon='play_arrow',
                                                on_click=lambda sid=servizio.id: inizializza_servizio_ui(
                                                    sid, carica_servizi_cliente
                                                ),
                                            ).classes('q-pa-sm')

                                        elif stato_servizio == 'IN_LAVORAZIONE':
                                            ui.button(
                                                'Inoltra al notaio',
                                                icon='send',
                                                on_click=lambda sid=servizio.id: inoltra_al_notaio_ui(
                                                    sid, carica_servizi_cliente
                                                ),
                                            ).classes('q-pa-sm')
                                            ui.button(
                                                'Modifica',
                                                icon='edit',
                                                on_click=lambda sid=servizio.id: ui.navigate.to(
                                                    f'/servizi/{sid}/modifica'
                                                ),
                                            ).classes('q-pa-sm')
                                            ui.button(
                                                'Elimina',
                                                icon='delete',
                                                on_click=lambda sid=servizio.id: elimina_servizio_ui(
                                                    sid, carica_servizi_cliente
                                                ),
                                            ).classes('q-pa-sm')

                                        elif stato_servizio in [
                                            'IN_ATTESA_APPROVAZIONE',
                                            'APPROVATO',
                                            'RIFIUTATO',
                                            'CONSEGNATO',
                                        ]:
                                            ui.button(
                                                'Visualizza',
                                                icon='visibility',
                                                on_click=lambda s=servizio: ui.navigate.to(
                                                    f'/servizi/{s.id}/dettagli'
                                                ),
                                            ).classes('q-pa-sm')

                def on_search_servizi(e=None):
                    q = (ricerca_servizi.value or '').strip().lower()
                    if not q or len(q) < SEARCH_MIN_LENGTH:
                        servizi_display[:] = servizi_originali[:]
                    else:
                        def match(s: Servizio):
                            tipo = s.tipo.value if hasattr(s.tipo, 'value') else (s.tipo or '')
                            codice = s.codiceServizio or s.codiceCorrente or ''
                            fields = " ".join([str(tipo), str(codice)]).lower()
                            return q in fields

                        servizi_display[:] = [s for s in servizi_originali if match(s)]
                    refresh_ui()

                ricerca_servizi.on('update:model-value', on_search_servizi)
                carica_servizi_cliente()

        dialog.open()

    # -------------------------
    # Funzioni client list
    # -------------------------
    def carica_clienti():
        nonlocal clienti_originali, miei_clienti_ids
        try:
            resp_miei = api_session.get('/studio/clienti?onlyMine=true')
            if resp_miei.status_code == 200:
                miei = resp_miei.json()
                miei_clienti_ids = {c.get('id') for c in miei if c}
            else:
                miei_clienti_ids = set()
        except Exception:
            miei_clienti_ids = set()

        try:
            if only_mine.value:
                resp = api_session.get('/studio/clienti?onlyMine=true')
            else:
                resp = api_session.get('/studio/clienti/')
            clienti_originali = resp.json() if resp.status_code == 200 else []
        except Exception as e:
            clienti_originali = []
            print(f"Errore caricamento clienti: {e}")

        val = (search.value or '').strip()
        if val and len(val) >= SEARCH_MIN_LENGTH:
            filtra_clienti(val)
        else:
            mostra_tutti_clienti()

    def mostra_tutti_clienti():
        clienti_display = clienti_originali[:]
        render_clienti(clienti_display)

    def filtra_clienti(testo_ricerca):
        testo = testo_ricerca.strip().lower()
        if not testo or len(testo) < SEARCH_MIN_LENGTH:
            mostra_tutti_clienti()
            return

        tokens = [t for t in testo.split() if t]

        def match(cli):
            nome = cli.get('utente', {}).get('nome', '')
            cognome = cli.get('utente', {}).get('cognome', '')
            email = cli.get('utente', {}).get('email', '')
            fields = ' '.join([str(nome), str(cognome), str(email)]).lower()
            words = fields.split()
            for token in tokens:
                if not any(w.startswith(token) for w in words):
                    return False
            return True

        clienti_display = [c for c in clienti_originali if match(c)]
        render_clienti(clienti_display)

    def render_clienti(clienti_display):
        clienti_list.clear()
        if not clienti_display:
            with clienti_list:
                ui.label('Nessun cliente trovato.').classes('text-grey-7 q-mt-md')
            return

        for cli in clienti_display:
            with clienti_list:
                with ui.card().style('background:#e3f2fd;border-radius:1em;min-height:78px;padding:1em 2em;'):
                    nome = cli.get('utente', {}).get('nome', '')
                    cognome = cli.get('utente', {}).get('cognome', '')
                    cliente_id = cli.get('id')

                    is_mio = cliente_id in miei_clienti_ids
                    title = f"{nome} {cognome}"
                    if is_mio:
                        title = f"{title}  •  MIO"

                    ui.label(title).classes('text-body1 q-mb-xs')

                    resp = cli.get('responsabile')
                    if resp:
                        rnome = resp.get('nome', '')
                        rcognome = resp.get('cognome', '')
                        ui.label(f"Responsabile: {rnome} {rcognome}").classes('text-caption text-grey-6')

                    with ui.row().style('gap:8px;'):
                        ui.button(
                            'Servizi',
                            icon='work',
                            color='primary',
                            on_click=lambda id=cliente_id, t=title: mostra_servizi_cliente_dialog(id, t),
                        ).props('flat round')
                        ui.button(
                            'Documenti',
                            icon='folder',
                            color='accent',
                            on_click=lambda id=cliente_id: visualizza_documenti(id),
                        ).props('flat round')
                        ui.button(
                            'Aggiungi',
                            icon='add',
                            color='positive',
                            on_click=lambda cid=cliente_id, n=title: open_crea_dialog_for_cliente(cid, n),
                        ).props('flat round')

    def open_crea_dialog_for_cliente(cliente_id, cliente_display):
        selected_cliente['id'] = cliente_id
        selected_cliente['display'] = cliente_display
        try:
            cliente_label.text = f"Cliente: {cliente_display} (id {cliente_id})"
        except Exception:
            pass
        crea_servizio_dialog.open()

    def visualizza_documenti(cliente_id):
        ui.navigate.to(f'/servizi_cliente/{cliente_id}/documenti')

    def on_search_change(e=None):
        val = search.value if search.value is not None else ''
        val = str(val).strip()
        if val == '' or len(val) < SEARCH_MIN_LENGTH:
            mostra_tutti_clienti()
        else:
            filtra_clienti(val)

    search.on('update:model-value', on_search_change)
    only_mine.on('click', lambda e=None: carica_clienti())

    carica_clienti()