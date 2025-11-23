from nicegui import ui
from app.api.api import api_session
from app.models.servizio import Servizio

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


def clienti_page():
    ui.label('Clienti').classes('text-h5 q-mt-xl q-mb-lg').style(
        'background:#1976d2;color:white;border-radius:2em;padding:.5em 2.5em;'
        'display:block;text-align:center;font-weight:600;letter-spacing:0.04em;'
    )

    # barra di ricerca
    search = ui.input('', placeholder="Cerca per nome o cognome...").props('outlined dense').style(
        'max-width:320px;margin-bottom:0;'
    )

    clienti_list = ui.column().classes('full-width').style('gap:18px;')

    clienti_originali = []   # tutti i clienti
    clienti_display = []     # clienti filtrati

    # ---- Dialog creazione servizio (notaio) ----
    crea_servizio_dialog = ui.dialog()
    crea_msg = None
    selected_cliente = {'id': None, 'display': ''}

    with crea_servizio_dialog:
        with ui.card().classes('q-pa-md').style('max-width:420px;'):
            ui.label('Crea nuovo servizio (approvato)').classes('text-h6 q-mb-md')
            cliente_label = ui.label('').classes('q-mb-sm')
            tipo_input = ui.select(TIPI_SERVIZIO, label="Tipo servizio").props("outlined dense").classes("q-mb-sm")
            codice_corrente_input = ui.input('Codice corrente (opzionale)').props('outlined dense').classes('q-mb-sm')
            crea_msg = ui.label().classes('text-negative q-mb-sm')

            def submit_crea():
                # validazioni
                if not selected_cliente.get('id'):
                    crea_msg.text = 'Cliente non selezionato'
                    return
                if not tipo_input.value:
                    crea_msg.text = 'Seleziona un tipo di servizio!'
                    return

                codice_raw = (codice_corrente_input.value or '').strip()
                try:
                    codice_val = int(codice_raw) if codice_raw != '' else None
                except Exception:
                    crea_msg.text = 'Codice corrente deve essere un numero intero'
                    return

                try:
                    cliente_for_nav = int(selected_cliente['id'])

                    # 1) crea servizio come fa il dipendente (codici gestiti dal backend)
                    res = api_session.crea_servizio(
                        cliente_for_nav,
                        tipo_input.value,
                        codice_corrente=codice_val,
                        dipendente_id=None,  # il notaio non è dipendente tecnico; puoi lasciare None
                    )

                    created_obj = None
                    created_id = None
                    if isinstance(res, dict):
                        created_obj = res
                    elif hasattr(res, 'json'):
                        created_obj = res.json()
                    if created_obj:
                        created_id = created_obj.get('id')

                    # 2) imposta subito stato APPROVATO
                    if created_id is not None:
                        patch_resp = api_session.patch(
                            f"/studio/servizi/{created_id}",
                            {"statoServizio": "APPROVATO"},
                        )
                        if patch_resp.status_code != 200:
                            crea_msg.text = f"Servizio creato ma errore nel set stato APPROVATO: {patch_resp.text}"
                            return

                    # estrai codice per notifica
                    codice_generato = None
                    try:
                        if created_obj:
                            codice_generato = created_obj.get('codiceServizio') or created_obj.get('codice_servizio')
                    except Exception:
                        codice_generato = None

                    if codice_generato:
                        ui.notify(f'Servizio creato e approvato! Codice: {codice_generato}', color='positive')
                    else:
                        ui.notify('Servizio creato e approvato!', color='positive')

                    # pulizia campi
                    tipo_input.value = None
                    codice_corrente_input.value = ''
                    cliente_display = selected_cliente.get('display', f'id {cliente_for_nav}')
                    selected_cliente['id'] = None
                    selected_cliente['display'] = ''
                    cliente_label.text = ''

                    crea_servizio_dialog.close()
                    # riapri subito i servizi del cliente
                    mostra_servizi_cliente_dialog(
                        cliente_for_nav,
                        cliente_display,
                        created_id=created_id,
                        created_obj=created_obj,
                    )
                except Exception as e:
                    crea_msg.text = f'Errore: {e}'
                    ui.notify(f'Errore creazione servizio: {e}', color='negative')

            with ui.row().classes('q-mt-md'):
                ui.button('Crea', on_click=submit_crea).classes('q-pa-md')
                ui.button('Annulla', on_click=lambda: crea_servizio_dialog.close()).classes('q-ml-md q-pa-md')

    # ---- Dialog servizi per cliente (notaio) ----
    def mostra_servizi_cliente_dialog(cliente_id: int, cliente_display: str, created_id=None, created_obj=None):
        dialog = ui.dialog()
        servizi_originali = []
        servizi_display_local = []
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
                    nonlocal servizi_originali, servizi_display_local
                    try:
                        resp = api_session.get(f'/studio/servizi?cliente_id={cliente_id}')
                        if resp.status_code == 200:
                            arr = resp.json()
                            filtered = [
                                s for s in arr
                                if not s.get('archived', False) and not s.get('is_deleted', False)
                            ]
                            servizi_originali = [Servizio.from_dict(s) for s in filtered]
                        else:
                            servizi_originali = []
                    except Exception as e:
                        print(f"[DEBUG] Errore caricamento servizi cliente {cliente_id}: {e}")
                        servizi_originali = []

                    # se abbiamo appena creato un servizio non ancora visibile, prova ad aggiungerlo in testa
                    try:
                        if created_id and not any(
                                getattr(s, 'id', None) == created_id
                                for s in servizi_originali
                        ):
                            if created_obj:
                                try:
                                    servizi_originali.insert(0, Servizio.from_dict(created_obj))
                                except Exception as e:
                                    print('[DEBUG] errore insert created_obj:', e)
                    except Exception as e:
                        print('[DEBUG] errore gestione created_id:', e)

                    servizi_display_local = servizi_originali[:]
                    refresh_ui()

                def refresh_ui():
                    servizi_container.clear()
                    if not servizi_display_local:
                        with servizi_container:
                            ui.label('Nessun servizio trovato per questo cliente.').classes('text-grey-7')
                        return

                    for servizio in servizi_display_local:
                        titolo_tipo = (
                            servizio.tipo.value if hasattr(servizio.tipo, 'value')
                            else (servizio.tipo or '')
                        )
                        codice_visualizzato = servizio.codiceServizio or servizio.codiceCorrente or 'N/A'
                        titolo = f"{titolo_tipo} (Codice: {codice_visualizzato})"

                        if hasattr(servizio.statoServizio, 'value'):
                            stato_str = str(servizio.statoServizio.value).upper()
                        else:
                            stato_str = (
                                str(servizio.statoServizio).upper()
                                if servizio.statoServizio is not None else 'N/A'
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
                                        on_click=lambda s=servizio: ui.navigate.to(f'/servizi_notaio/{s.id}/dettagli'),
                                    ).classes('q-pa-sm')
                                    ui.button(
                                        'Archivia',
                                        icon='archive',
                                        on_click=lambda sid=servizio.id: archivia_servizio_ui(
                                            sid, carica_servizi_cliente
                                        ),
                                    ).classes('q-pa-sm')

                                    # Notaio: puoi permettere modifica/elimina anche qui se vuoi
                                    ui.button(
                                        'Elimina',
                                        icon='delete',
                                        on_click=lambda sid=servizio.id: elimina_servizio_ui(
                                            sid, carica_servizi_cliente
                                        ),
                                    ).classes('q-pa-sm')

                def on_search_servizi(e=None):
                    q = (ricerca_servizi.value or '').strip().lower()
                    if not q or len(q) < SEARCH_MIN_LENGTH:
                        local = servizi_originali[:]
                    else:
                        def match(s: Servizio):
                            tipo = s.tipo.value if hasattr(s.tipo, 'value') else (s.tipo or '')
                            codice = s.codiceServizio or s.codiceCorrente or ''
                            fields = " ".join([str(tipo), str(codice)]).lower()
                            return q in fields

                        local = [s for s in servizi_originali if match(s)]
                    nonlocal servizi_display_local
                    servizi_display_local = local
                    refresh_ui()

                ricerca_servizi.on('update:model-value', on_search_servizi)
                carica_servizi_cliente()

        dialog.open()

    # ---- Azioni comuni servizi (archivia / elimina) ----
    def archivia_servizio_ui(servizio_id: int, carica_callback=None):
        try:
            api_session.archivia_servizio(servizio_id)
            ui.notify("Servizio archiviato!", color="positive")
            if carica_callback:
                carica_callback()
        except Exception as e:
            ui.notify(f"Errore archiviazione: {e}", color="negative")

    def elimina_servizio_ui(servizio_id: int, carica_callback=None):
        try:
            api_session.elimina_servizio(servizio_id)
            ui.notify("Servizio eliminato!", color="positive")
            if carica_callback:
                carica_callback()
        except Exception as e:
            ui.notify(f"Errore eliminazione: {e}", color="negative")

    # ---- Lista clienti ----
    def carica_clienti():
        nonlocal clienti_originali
        try:
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
        nonlocal clienti_display
        clienti_display = clienti_originali[:]
        render_clienti()

    def filtra_clienti(testo_ricerca):
        nonlocal clienti_display
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
        render_clienti()

    def render_clienti():
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
                    title = f"{nome} {cognome}"

                    ui.label(title).classes('text-body1 q-mb-xs')

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
            # cliente_label è chiuso nel dialog; lo abbiamo definito lì sopra
            # usiamo nonlocal per la closure oppure catturiamo cliente_label
            pass
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
    carica_clienti()