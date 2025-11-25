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

    # ---- CSS personalizzato ----
    ui.add_head_html('''
<style>
/* Titolo della pagina */
.clienti-title {
    color:#1976d2;
    padding: 0.6em 2.8em;
    font-weight: 700;
    letter-spacing: 0.05em;
    display: block;
    text-align: center;
    margin: 2em auto 1.5em auto;
    width: fit-content;
    font-size: 32px;
}

/* Barra di ricerca */
.search-bar {
    width: 600px;
    max-width: 100%;
    margin: 0 auto 20px auto;
    border-radius: 30px;
    background: #fff;
    border: 2px solid #ccc;
    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
    padding: 8px 16px;
    transition: all 0.18s ease;
}
.search-bar input {
    border: none !important;
    outline: none !important;
    background: transparent !important;
    font-size: 1.1rem !important;
    font-weight: 500 !important;
    color: #333 !important;
}
.search-bar input::placeholder { 
    color: #888; 
    font-size: 1.1rem; 
}
.search-bar:focus-within { 
    border-color: #2196f3; 
    box-shadow: 0 0 8px rgba(33,150,243,0.18); 
}

/* Card principale */
.q-card.main-card {
    background: #f0f0f0;
    border-radius: 18px;
    padding: 40px 20px;
    width: 50%;
    max-width: 1000px;
    margin: 60px auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-sizing: border-box;
}

/* Lista clienti */
.clienti-list-container {
    display: flex;
    flex-direction: column;
    align-items: center; /* centra le card */
    gap: 16px;
    width: 100%;
}

/* Card singolo cliente */
.client-card {
    background: #e3f2fd;
    border-radius: 0.8em;
    min-height: 60px;
    padding: 1em 2em;
    width: 90%;
    max-width: 600px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
}

/* Pulsanti card cliente */
.client-card .q-btn { 
    border-radius: 12px; 
    font-weight: 600; 
    min-width: 120px; 
}
.custom-button-blue-light-panels {
    display: flex !important;
    background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 2.5em !important;
    padding: 0.2em 1.2em !important;
    font-size: 1.2rem !important;
    width: 150px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    letter-spacing: 0.5px !important;
    padding: 0.2em 1.2em !important;
}

/* Responsività */
@media (max-width: 720px) {
    .q-card.main-card { width: 92%; padding: 20px; }
    .client-card { width: 95%; padding: 0.8em 1em; }
    .client-card .q-btn { min-width: 100px; }
}
</style>
    ''')

    with ui.card().classes('main-card'):
        ui.label('CLIENTI').classes('text-h5 q-mt-xl q-mb-lg clienti-title').style(
            'color:#1976d2;padding:.5em 2.5em;'
            'text-align:center;font-weight:600;letter-spacing:0.04em;'
        )

        # barra di ricerca
        search = ui.input('', placeholder="Cerca per nome o cognome...").classes('search-bar q-mb-sm') \
            .props('dense borderless') \
            .style('margin-bottom:0;')

        clienti_list = ui.column().classes('justify-center items-center full-width').style('gap:18px;')

        clienti_originali = []   # tutti i clienti
        clienti_display = []     # clienti filtrati

        # ---- Dialog creazione servizio (notaio) ----
        crea_servizio_dialog = ui.dialog()
        crea_msg = None
        selected_cliente = {'id': None, 'display': ''}

        with crea_servizio_dialog:
            with ui.card().classes('q-pa-md').style('max-width:400px;width:100%; align-items:center;border-radius:12px;background-color: #FFF8E7; padding: 0.5rem !important;'):
                ui.label('Crea servizio').classes('text-h6 q-mb-md').style('color:#1976d2;padding: 0.6em 2.8em;font-weight: 700;letter-spacing: 0.05em;display: block;text-align: center;width: fit-content;font-size: 24px;')
                cliente_label = ui.label('').classes('q-mb-sm')
                with ui.row().classes('q-pa-sm').style('align-items:center'):
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

                        # parsing difensivo della risposta create
                        created_obj = None
                        created_id = None
                        if isinstance(res, dict):
                            created_obj = res
                        elif hasattr(res, 'json'):
                            try:
                                created_obj = res.json()
                            except Exception:
                                created_obj = None
                        if created_obj:
                            created_id = created_obj.get('id')

                        # 2) imposta subito stato APPROVATO (controllo difensivo)
                        if created_id is not None:
                            patch_resp = api_session.patch(
                                f"/studio/servizi/{created_id}",
                                {"statoServizio": "APPROVATO"},
                            )
                            if getattr(patch_resp, 'status_code', None) != 200:
                                text = getattr(patch_resp, 'text', None)
                                try:
                                    if text is None and hasattr(patch_resp, 'json'):
                                        text = patch_resp.json()
                                except Exception:
                                    text = str(patch_resp)
                                crea_msg.text = f"Servizio creato ma errore nel set stato APPROVATO: {text}"
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

                with ui.row().classes('q-mt-md').style('align-items:center;width:100%;justify-content:center;'):
                    ui.button('Crea', on_click=submit_crea).classes('custom-button-blue-light-panels')
                    ui.button('Annulla', on_click=lambda: crea_servizio_dialog.close()).classes('custom-button-blue-light-panels')

        # ---- Dialog servizi per cliente (notaio) ----
        def mostra_servizi_cliente_dialog(cliente_id: int, cliente_display: str, created_id=None, created_obj=None):
            dialog = ui.dialog()
            servizi_originali = []
            servizi_display_local = []
            servizi_container = None

            def open_edit_servizio_dialog(servizio: Servizio, refresh_callback=None):
                """Apre un dialog inline per modificare un singolo servizio e salvarlo via PATCH."""
                dlg = ui.dialog()
                with dlg:
                    with ui.card().classes('q-pa-md').style('max-width:480px'):
                        ui.label(f"Modifica servizio #{getattr(servizio, 'id', '—')}").classes('text-h6 q-mb-md')

                        # prefill tipo
                        tipo_val = None
                        try:
                            tipo_val = servizio.tipo.value if hasattr(servizio.tipo, 'value') else servizio.tipo
                        except Exception:
                            tipo_val = getattr(servizio, 'tipo', None)
                        tipo_sel = ui.select(TIPI_SERVIZIO, label='Tipo').props('outlined dense')
                        if tipo_val is not None:
                            tipo_sel.value = tipo_val

                        # prefill codice
                        codice_val = getattr(servizio, 'codiceCorrente', None) or getattr(servizio, 'codiceServizio', '') or ''
                        codice_inp = ui.input(label='Codice corrente (opz.)').props('outlined dense')
                        codice_inp.value = codice_val

                        # prefill dipendente id (se possibile)
                        dip_val = None
                        try:
                            if hasattr(servizio, 'dipendenti') and servizio.dipendenti:
                                first = servizio.dipendenti[0]
                                dip_val = getattr(first, 'id', None)
                            elif hasattr(servizio, 'dipendente_id'):
                                dip_val = getattr(servizio, 'dipendente_id')
                        except Exception:
                            dip_val = None
                        dip_inp = ui.input(label='Dipendente ID (opz.)').props('outlined dense')
                        dip_inp.value = dip_val or ''

                        status_lbl = ui.label().classes('text-caption text-grey-6 q-mt-sm')

                        def do_save():
                            payload = {}
                            t = tipo_sel.value
                            if t:
                                payload['tipo'] = t

                            # codice
                            raw_cod = codice_inp.value
                            codice_raw = ''
                            if raw_cod is None:
                                codice_raw = ''
                            elif isinstance(raw_cod, str):
                                codice_raw = raw_cod.strip()
                            else:
                                try:
                                    codice_raw = str(raw_cod).strip()
                                except Exception:
                                    codice_raw = ''
                            if codice_raw != '':
                                try:
                                    payload['codiceCorrente'] = int(codice_raw)
                                except Exception:
                                    payload['codiceCorrente'] = codice_raw

                            # dipendente
                            dipv = dip_inp.value
                            if dipv is not None and dipv != '':
                                if isinstance(dipv, (int, float)):
                                    try:
                                        payload['dipendente_id'] = int(dipv)
                                    except Exception:
                                        payload['dipendente_id'] = dipv
                                else:
                                    ds = str(dipv).strip()
                                    if ds != '':
                                        try:
                                            payload['dipendente_id'] = int(ds)
                                        except Exception:
                                            payload['dipendente_id'] = ds

                            if not payload:
                                status_lbl.text = 'Nessuna modifica da salvare'
                                return

                            try:
                                resp = api_session.patch(f'/studio/servizi/{getattr(servizio, "id")}', payload)
                                status = getattr(resp, 'status_code', None)
                                # gestione difensiva: considera anche dict come successo
                                if status is None and isinstance(resp, dict):
                                    ui.notify('Modifica salvata', color='positive')
                                    dlg.close()
                                    if callable(refresh_callback):
                                        refresh_callback()
                                    return
                                if status == 200:
                                    ui.notify('Modifica salvata', color='positive')
                                    dlg.close()
                                    if callable(refresh_callback):
                                        refresh_callback()
                                else:
                                    err = ''
                                    try:
                                        err = resp.text if hasattr(resp, 'text') else str(resp)
                                    except Exception:
                                        try:
                                            err = resp.json()
                                        except Exception:
                                            err = str(resp)
                                    status_lbl.text = f'Errore: {err}'
                                    ui.notify(f'Errore salvataggio: {err}', color='negative')
                            except Exception as e:
                                status_lbl.text = f'Errore: {e}'
                                ui.notify(f'Errore salvataggio: {e}', color='negative')

                        with ui.row().classes('q-mt-md').style('gap:8px'):
                            ui.button('Salva', on_click=do_save).classes('q-pa-md')
                            ui.button('Annulla', on_click=dlg.close).classes('q-ml-md q-pa-md')

                dlg.open()

            with dialog:
                with ui.card().classes('q-pa-xl').style('max-width:1000px;width: 1000px;background: rgba(240,240,240) !important;box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important;border-radius: 2.5em !important;border: 1.7px solid #e3eaf1 !important;backdrop-filter: blur(6px);align-items: center;'):
                    ui.label(f'Servizi di {cliente_display} (id {cliente_id})').classes('text-h6 q-mb-md').style('color:#1976d2;padding: 0.6em 2.8em;font-weight: 700;letter-spacing: 0.05em;display: block;text-align: center;width: fit-content;font-size: 24px;')
                    with ui.row().classes('q-mb-md'):
                        ricerca_servizi = ui.input('', placeholder="Cerca servizio (tipo / codice)...").props(
                            'outlined dense'
                        ).style('max-width:420px;')
                        ui.button('Aggiorna', icon='refresh', on_click=lambda: carica_servizi_cliente()).props('flat')

                    servizi_container = ui.column().classes('full-width').style('gap:12px; align-items:flex-start; max-height:400px; overflow-y:auto;')

                    def carica_servizi_cliente():
                        nonlocal servizi_originali, servizi_display_local
                        try:
                            resp = api_session.get(f'/studio/servizi?cliente_id={cliente_id}')
                            if getattr(resp, 'status_code', None) == 200:
                                try:
                                    arr = resp.json()
                                except Exception:
                                    arr = resp if isinstance(resp, list) else []
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

                            with servizi_container.style('align-items:center;'):
                                with ui.card().classes('q-pa-md q-mb-sm').style('background:#e0f7fa; border-radius:1em; padding:0.5em 2em; width:92%;margin-top: 2em;'):
                                    ui.label(titolo).classes('text-h6 q-mb-sm')
                                    with ui.row().classes('items-center q-gutter-xs'):
                                        ui.icon(get_icon_for_stato(stato_str), size='24px').classes('q-mr-xs')
                                        ui.label(f"Stato: {stato_str}").classes('text-subtitle2 q-mb-xs')

                                    with ui.row().classes('q-gutter-md q-mt-sm'):
                                        ui.button(
                                            'Dettagli',
                                            icon='visibility',
                                            color='primary',
                                            on_click=lambda s=servizio: ui.navigate.to(f'/servizi_notaio/{s.id}/dettagli'),
                                        ).props('flat round type="button"')
                                        ui.button(
                                            'Documentazione',
                                            icon='folder',
                                            color='accent',
                                            on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti'),
                                        ).props('flat round type="button"')
                                        ui.button(
                                            'Archivia',
                                            icon='archive',
                                            color='secondary',
                                            on_click=lambda sid=servizio.id: archivia_servizio_ui(
                                                sid, carica_servizi_cliente
                                            ),
                                        ).props('flat round type="button"')

                                        # Notaio: elimina rimane disponibile
                                        ui.button(
                                            'Elimina',
                                            icon='delete',
                                            color='negative',
                                            on_click=lambda sid=servizio.id: elimina_servizio_ui(
                                                sid, carica_servizi_cliente
                                            ),
                                        ).props('flat round type="button"')

                                        # MOSTRO Modifica per TUTTI i servizi (apre dialog inline)
                                        ui.button(
                                            'Modifica',
                                            icon='edit',
                                            color='secondary',
                                            on_click=lambda s=servizio: open_edit_servizio_dialog(s, refresh_callback=carica_servizi_cliente),
                                        ).props('flat round type="button"')

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
            if getattr(resp, 'status_code', None) == 200:
                try:
                    clienti_originali = resp.json()
                except Exception:
                    clienti_originali = resp if isinstance(resp, list) else []
            else:
                clienti_originali = []
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
                with ui.card().classes('justify-center items-center cliente-card').style('background:#e3f2fd;border-radius:1em;min-height:78px;padding:1em 2em;'):
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
            # se vuoi aggiornare cliente_label dall'esterno devi rimandare il valore o usare closure/nonlocal
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