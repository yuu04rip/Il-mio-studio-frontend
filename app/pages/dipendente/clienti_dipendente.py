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

    # ---- CSS personalizzato ----
    ui.add_head_html('''
    <style>
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
.text-h6 {
    color:#1976d2;
    padding: 0.6em 2.8em;
    font-weight: 700;
    letter-spacing: 0.05em;
    display: block;
    text-align: center;
    width: fit-content;
    font-size: 24px;
            }
        
.search-bar {
    width: 600px;
    max-width: 100%;
    margin: 0 auto;
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
.search-bar input::placeholder { color:#888; font-size:1.1rem; }
.search-bar:focus-within { border-color:#2196f3; box-shadow:0 0 8px rgba(33,150,243,0.18); }

.q-card.main-card {
    background:#f0f0f0;
    border-radius: 18px;
    padding: 20px;
    width: 50%;
    max-width: 1000px;
    margin: 60px auto;
    display:flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.client-card {
    background:#e3f2fd;
    border-radius:0.8em;
    min-height:50px;
    padding:0.5em 1.2em;
    margin-bottom: 8px;
    width:100%;
    box-shadow:0 2px 6px rgba(0,0,0,0.06);
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
.client-card .q-btn { border-radius:12px; min-width:120px; font-weight:600; }
@media (max-width:720px) {
    .q-card.main-card { width:92%; padding:14px; }
    </style>
    ''')

    with ui.row().classes('justify-center items-center').style('width:100%; margin-top:2em;'):
        # main card wrapper: (solo presentazione, non tocca la logica)
        with ui.card().classes('main-card'):
            ui.label('CLIENTI').classes('text-h5 q-mt-xl q-mb-lg clienti-title').style(
                'color:#1976d2;padding:.5em 2.5em;'
                'text-align:center;font-weight:600;letter-spacing:0.04em;'
            )

            # mostra il nome del dipendente (se disponibile in api_session.user)
            user = getattr(api_session, 'user', None) or {}
            user_nome = user.get('nome') or user.get('username') or ''
            user_cognome = user.get('cognome') or ''
            if user_nome or user_cognome:
                ui.label(f'Operatore: {user_nome} {user_cognome}').classes('text-subtitle2 q-mb-sm')

            # tenta di recuperare dipendente_id (utile per la creazione del servizio e per mostrare azioni)
            try:
                # api_session.get_dipendente_id_by_user può restituire direttamente un int oppure una Response-like
                dipendente_id = None
                if user and user.get('id'):
                    resp = api_session.get_dipendente_id_by_user(user['id'])
                    # gestione difensiva: se è un dict/number o response-like
                    try:
                        if isinstance(resp, dict):
                            dipendente_id = resp.get('id') or resp.get('dipendente_id') or resp.get('result')
                        elif isinstance(resp, int):
                            dipendente_id = resp
                        elif hasattr(resp, 'status_code') and getattr(resp, 'status_code') in (200, 201):
                            try:
                                body = resp.json()
                                # endpoint restituisce int or {"id": int}
                                if isinstance(body, dict):
                                    dipendente_id = body.get('id') or body.get('dipendente_id') or body.get('result')
                                elif isinstance(body, int):
                                    dipendente_id = body
                            except Exception:
                                # potrebbe essere un intero raw
                                try:
                                    dipendente_id = int(resp.text)
                                except Exception:
                                    dipendente_id = None
                        else:
                            # fallback: se la funzione restituisce direttamente un int
                            try:
                                dipendente_id = int(resp)
                            except Exception:
                                dipendente_id = None
                    except Exception:
                        dipendente_id = None
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
                with ui.card().classes('q-pa-md').style('max-width:400px;width:100%; align-items:center;border-radius:12px;background-color: #FFF8E7; padding: 0.5rem !important; '):
                    ui.label('Crea servizio').classes('text-h6 q-mb-md')
                    cliente_label = ui.label('').classes('q-mb-sm')
                    with ui.row().classes('q-pa-sm').style('align-items:center'):
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
                            # usiamo l'helper creato nel client api_session; se non disponibile fallback a post
                            try:
                                res = api_session.crea_servizio(
                                    cliente_for_nav,
                                    tipo_input.value,
                                    codice_corrente=codice_val,
                                    dipendente_id=dipendente_id,
                                )
                            except Exception:
                                # fallback: invio payload esplicito al POST /studio/servizi
                                payload = {
                                    "cliente_id": cliente_for_nav,
                                    "tipo": tipo_input.value,
                                    "codiceCorrente": codice_val,
                                    "dipendente_id": dipendente_id,
                                }
                                res = api_session.post('/studio/servizi', json=payload)

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
                                elif hasattr(res, 'status_code') and getattr(res, 'status_code') in (200, 201):
                                    try:
                                        created_obj = res.json()
                                    except Exception:
                                        created_obj = None
                                elif hasattr(res, 'json'):
                                    try:
                                        created_obj = res.json()
                                    except Exception:
                                        created_obj = None
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

                            # IMPORTANT: ricarica i clienti così la UI aggiorna "Personali"
                            try:
                                carica_clienti()
                            except Exception as e:
                                print('[DEBUG] errore carica_clienti dopo creazione:', e)

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

                    with ui.row().classes('q-mt-md btn-aggiungi').style('align-items:center;width:100%;justify-content:center;'):
                        ui.button('Crea', on_click=submit_crea).classes('custom-button-blue-light-panels')
                        ui.button('Annulla', on_click=lambda: crea_servizio_dialog.close()).classes('custom-button-blue-light-panels')

            # ------------------------------
            # BARRA DI RICERCA
            # ------------------------------
            with ui.row():
                search = ui.input('', placeholder="Cerca per nome o cognome...").classes('search-bar q-mb-sm') \
                    .props('dense borderless') \
                    .style('margin-bottom:0;')

            # ------------------------------
            # SOLO I MIEI + AGGIORNA SOTTO
            # ------------------------------
            with ui.row().classes('items-center q-mb-md').style('gap:12px; justify-content:center;'):
                only_mine = ui.checkbox('Personali', value=True).props('dense')
                ui.button('Aggiorna', icon='refresh', on_click=lambda: carica_clienti()).props('flat')


            # area risultati
            clienti_list = ui.column().classes('full-width justify-center items-center').style('gap:18px;')

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
            res = api_session.inizializza_servizio(servizio_id)
            # gestione difensiva: se response-like, controlla code
            ok = False
            try:
                if hasattr(res, 'status_code'):
                    ok = getattr(res, 'status_code') in (200, 201)
                elif isinstance(res, dict):
                    ok = True
            except Exception:
                ok = True
            if ok:
                ui.notify("Servizio inizializzato!", color="positive")
                # ricarica clienti e servizi
                if carica_callback:
                    carica_callback()
                try:
                    carica_clienti()
                except Exception:
                    pass
            else:
                ui.notify("Errore inizializzazione servizio", color="negative")
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
        ui.add_head_html("""
<style>
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;  /* larghezza scrollbar */
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;  /* elimina il bordo bianco */
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: rgba(25,118,210,0.5);  /* colore della “barra” */
    border-radius: 3px;
    border: none;  /* rimuove eventuale bordo */
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
.text-h6 {
    color:#1976d2;
    padding: 0.6em 2.8em;
    font-weight: 700;
    letter-spacing: 0.05em;
    display: block;
    text-align: center;
    width: fit-content;
    font-size: 24px;
            }
</style>
""")
        print('[DEBUG] mostra_servizi_cliente_dialog aperto per cliente_id=', cliente_id)
        dialog = ui.dialog()
        servizi_originali = []
        servizi_display = []
        servizi_container = None

        # Reinserisco qui la versione inline di edit (open_edit_servizio_dialog)
        def open_edit_servizio_dialog(servizio: Servizio, refresh_callback=None):
            """Apre un dialog inline per modificare il servizio e salvarlo via PATCH.
            Dopo il salvataggio richiama refresh_callback() se fornito."""
            dlg = ui.dialog()
            with dlg:
                with ui.card().classes('q-pa-md').style('max-width:400px;width:100%; align-items:center;border-radius:12px;background-color: #FFF8E7; padding: 0.5rem !important;'):
                    ui.label(f"Modifica servizio #{getattr(servizio, 'id', '—')}").classes('text-h6 q-mb-md')
                    # Prefill values
                    tipo_val = None
                    try:
                        tipo_val = servizio.tipo.value if hasattr(servizio.tipo, 'value') else servizio.tipo
                    except Exception:
                        tipo_val = getattr(servizio, 'tipo', None)
                    tipo_sel = ui.select(TIPI_SERVIZIO, label='Tipo').props('outlined dense')
                    if tipo_val is not None:
                        tipo_sel.value = tipo_val

                    codice_val = getattr(servizio, 'codiceCorrente', None) or getattr(servizio, 'codiceServizio', '') or ''
                    codice_inp = ui.input(label='Codice corrente (opz.)').props('outlined dense').style('width:80%')
                    codice_inp.value = codice_val

                    # try to extract a primary dipendente id (if present)
                    dip_val = None
                    try:
                        if hasattr(servizio, 'dipendenti') and servizio.dipendenti:
                            first = servizio.dipendenti[0]
                            dip_val = getattr(first, 'id', None)
                        elif hasattr(servizio, 'dipendente_id'):
                            dip_val = getattr(servizio, 'dipendente_id')
                    except Exception:
                        dip_val = None
                    dip_inp = ui.input(label='Dipendente ID (opz.)').props('outlined dense').style('width:80%')
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
                            # usa PATCH verso lo stesso prefisso usato nel frontend (/studio/servizi/...)
                            resp = api_session.patch(f'/studio/servizi/{getattr(servizio, "id")}', payload)
                            status = getattr(resp, 'status_code', None)
                            # gestione difensiva come nella "prima" versione: considera anche dict come successo
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
                                print('[DEBUG] PATCH non ok:', status, err)
                        except Exception as e:
                            status_lbl.text = f'Errore: {e}'
                            ui.notify(f'Errore salvataggio: {e}', color='negative')
                            print('[DEBUG] eccezione patch servizio:', e)

                    with ui.row().classes('q-mt-md').style('align-items:center;width:100%;justify-content:center;'):
                        ui.button('Salva', on_click=do_save).classes('custom-button-blue-light-panels')
                        ui.button('Annulla', on_click=dlg.close).classes('custom-button-blue-light-panels')

            dlg.open()

        with dialog:
            with ui.card().classes('q-pa-xl').style('max-width:1000px;width: 1000px;background: rgba(240,240,240) !important;box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important;border-radius: 2.5em !important;border: 1.7px solid #e3eaf1 !important;backdrop-filter: blur(6px);align-items: center;'):
                ui.label(f'Servizi di {cliente_display} (id {cliente_id})').classes('text-h6 q-mb-md')
                with ui.row().classes('q-mb-md'):
                    ricerca_servizi = ui.input('', placeholder="Cerca servizio (tipo / codice)...").props(
                        'outlined dense'
                    ).style('max-width:450px;')
                    ui.button('Aggiorna', icon='refresh', on_click=lambda: carica_servizi_cliente()).props('flat')
                servizi_container = ui.column().classes('full-width').style('gap:12px; align-items:flex-start; max-height:400px; overflow-y:auto;')

                def carica_servizi_cliente():
                    nonlocal servizi_originali, servizi_display
                    servizi_originali = []
                    servizi_display = []
                    try:
                        print('[DEBUG] chiamata GET /studio/servizi?cliente_id=', cliente_id)
                        resp = api_session.get(f'/studio/servizi?cliente_id={cliente_id}')
                        print('[DEBUG] status servizi cliente:', getattr(resp, 'status_code', None))
                        if getattr(resp, 'status_code', None) == 200:
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
                            print('[DEBUG] risposta non 200 servizi cliente:', getattr(resp, 'text', str(resp)))
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

                        with servizi_container.style('align-items:center;'):
                            with ui.card().classes('q-pa-md q-mb-sm').style(
                                    'background:#e0f7fa; border-radius:1em; padding:0.5em 2em; width:92%;margin-top: 2em;'
                            ):
                                ui.label(titolo).classes('text-subtitle1 text-dark text-weight-bold').style('text-align: left;')
                                with ui.row().classes('items-center q-gutter-xs'):
                                    ui.icon(get_icon_for_stato(stato_str), size='24px').classes('q-mr-xs')
                                    ui.label(f"Stato: {stato_str}").classes('text-subtitle2 q-mb-xs')

                                with ui.row().classes('q-gutter-md q-mt-sm'):
                                    ui.button(
                                        'Dettagli',
                                        icon='visibility',
                                        color='primary',
                                        on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/dettagli'),
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

                                    # MOSTRO Modifica per TUTTI i servizi (senza filtro di stato)
                                    ui.button(
                                        'Modifica',
                                        icon='edit',
                                        on_click=lambda s=servizio: open_edit_servizio_dialog(s, refresh_callback=carica_servizi_cliente),
                                    ).props('flat round type="button"')

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
                                                color='positive',
                                                on_click=lambda sid=servizio.id: inizializza_servizio_ui(
                                                    sid, carica_servizi_cliente
                                                ),
                                            ).props('flat round type="button"')

                                        elif stato_servizio == 'IN_LAVORAZIONE':
                                            ui.button(
                                                'Inoltra al notaio',
                                                icon='send',
                                                color='info',
                                                on_click=lambda sid=servizio.id: inoltra_al_notaio_ui(
                                                    sid, carica_servizi_cliente
                                                ),
                                            ).props('flat round type="button"')
                                            ui.button(
                                                'Elimina',
                                                icon='delete',
                                                color='negative',
                                                on_click=lambda sid=servizio.id: elimina_servizio_ui(
                                                    sid, carica_servizi_cliente
                                                ),
                                            ).props('flat round type="button"')

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
            if getattr(resp_miei, 'status_code', None) == 200:
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
            clienti_originali = resp.json() if getattr(resp, 'status_code', None) == 200 else []
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
                with ui.card().classes('justify-center items-center cliente-card').style('background:#e3f2fd;border-radius:1em;min-height:78px;padding:1em 2em;'):
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
                        ).props('flat round').classes('uniform-btn')
                        ui.button(
                            'Documenti',
                            icon='folder',
                            color='accent',
                            on_click=lambda id=cliente_id: visualizza_documenti(id),
                        ).props('flat round').classes('uniform-btn')
                        ui.button(
                            'Aggiungi',
                            icon='add',
                            color='positive',
                            on_click=lambda cid=cliente_id, n=title: open_crea_dialog_for_cliente(cid, n),
                        ).props('flat round').classes('uniform-btn')

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