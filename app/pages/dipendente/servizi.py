from nicegui import ui
from app.api.api import api_session
from app.models.servizio import Servizio

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

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        with ui.row().classes('items-center q-mb-md'):
            ui.icon('engineering', size='40px').classes('q-mr-md')
            ui.label('SERVIZI DA SVOLGERE').classes(
                'text-h5').style('background:#1a237e;color:white;border-radius:2em;padding:.5em 2em;')
            search_box = ui.input('', placeholder="Cerca servizio...").props(
                'dense').classes('q-ml-md').style('max-width:200px;')
            ui.button('Crea Servizio', icon='add',
                      on_click=lambda: crea_servizio_dialog.open()).classes('q-ml-lg q-pa-md')

        servizi = []
        servizi_altri = []
        servizi_approvati_disponibili = []

        servizi_container = ui.column().classes('full-width').style('gap:18px;')
        servizi_altri_container = ui.column().classes('full-width').style('gap:18px;')
        servizi_approvati_container = ui.column().classes('full-width').style('gap:18px;')

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
                        refresh_servizi(search_box.value)
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
            nonlocal servizi, servizi_altri, servizi_approvati_disponibili
            servizi.clear()
            servizi_altri.clear()
            servizi_approvati_disponibili.clear()
            try:
                res_creati = api_session.visualizza_lavoro_da_svolgere(dipendente_id)
                res_in_lavorazione = api_session.visualizza_servizi_inizializzati(dipendente_id)
                res_completati = api_session.visualizza_servizi_completati(dipendente_id)
                res_altri = api_session.get_altri_servizi(dipendente_id)
                res_approvati = api_session.visualizza_servizi_approvati()

                for r in [res_creati, res_in_lavorazione, res_completati]:
                    if isinstance(r, list):
                        servizi.extend([Servizio.from_dict(s) for s in r])

                if isinstance(res_altri, list):
                    servizi_altri.extend([Servizio.from_dict(s) for s in res_altri])

                miei_servizi_ids = {s.id for s in servizi}
                if isinstance(res_approvati, list):
                    for s in res_approvati:
                        assigned_ids = [
                            d['id'] if isinstance(d, dict) and 'id' in d else d
                            for d in s.get('dipendenti', [])
                        ]
                        if dipendente_id not in assigned_ids and s['id'] not in miei_servizi_ids:
                            servizi_approvati_disponibili.append(Servizio.from_dict(s))
            except Exception as e:
                print(f"Errore caricamento servizi: {e}")

        def elimina_servizio(servizio_id):
            try:
                api_session.elimina_servizio(servizio_id)
                ui.notify("Servizio eliminato!", color="positive")
                servizi[:] = [s for s in servizi if s.id != servizio_id]
                refresh_servizi(search_box.value)
            except Exception as e:
                ui.notify(f"Errore eliminazione: {e}", color="negative")

        def inoltra_servizio_notaio(servizio_id):
            try:
                api_session.inoltra_servizio_notaio(servizio_id)
                ui.notify("Servizio inoltrato al notaio!", color="positive")
                carica_tutti_servizi()
                refresh_servizi(search_box.value)
            except Exception as e:
                ui.notify(str(e), color="negative")

        def inizializza_servizio(servizio_id):
            try:
                api_session.inizializza_servizio(servizio_id)
                ui.notify("Servizio inizializzato!", color="positive")
                carica_tutti_servizi()
                refresh_servizi(search_box.value)
            except Exception as e:
                ui.notify(str(e), color="negative")

        def refresh_servizi(filter_text=""):
            servizi_container.clear()
            filtered = [s for s in servizi if not getattr(s, "is_deleted", False)]
            if filter_text:
                filtered = [s for s in filtered if filter_text.lower() in s.tipo.lower()
                            or filter_text.lower() in str(s.codiceServizio)]
            if not filtered:
                with servizi_container:
                    ui.label('Nessun servizio trovato.').classes(
                        "text-grey-7 q-mt-md").style("text-align:center;font-size:1.12em;")
                return

            for servizio in filtered:
                with servizi_container:
                    card_style = 'background:#e0f7fa;'
                    stato = str(servizio.statoServizio).lower()
                    if stato == 'approvato':
                        card_style = 'background:#e8f5e8;'
                    elif stato == 'rifiutato':
                        card_style = 'background:#ffebee;'
                    elif stato == 'consegnato':
                        card_style = 'background:#f3e5f5;'

                    with ui.card().classes('q-pa-md q-mb-md').style(card_style):
                        ui.label(f"{servizio.tipo} (Codice: {servizio.codiceServizio})").classes('text-h6 q-mb-sm')
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
                                ui.button('Visualizza dettagli', icon='visibility', on_click=lambda s=servizio: ui.navigate.to(f'/servizio_dettagli/{s.id}'))
                            ui.button('Documentazione', icon='folder', on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti')).classes('q-pa-md')

        def refresh_servizi_altri(filter_text=""):
            servizi_altri_container.clear()
            filtered = [s for s in servizi_altri if not getattr(s, "is_deleted", False)]
            if filter_text:
                filtered = [s for s in filtered if filter_text.lower() in s.tipo.lower()
                            or filter_text.lower() in str(s.codiceServizio)]
            if not filtered:
                with servizi_altri_container:
                    ui.label('Nessun servizio collaborato trovato.').classes(
                        "text-grey-7 q-mt-md").style("text-align:center;font-size:1.12em;")
                return
            for servizio in filtered:
                with servizi_altri_container:
                    ui.label(f"{servizio.tipo} (Codice: {servizio.codiceServizio})").classes('text-h6 q-mb-sm')
                    ui.button('Documentazione', icon='folder', on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti')).classes('q-pa-md')

        def refresh_servizi_approvati_disponibili(filter_text=""):
            servizi_approvati_container.clear()
            filtered = [s for s in servizi_approvati_disponibili if not getattr(s, "is_deleted", False)]
            if filter_text:
                filtered = [s for s in filtered if filter_text.lower() in s.tipo.lower()
                            or filter_text.lower() in str(s.codiceServizio)]
            if not filtered:
                with servizi_approvati_container:
                    ui.label('Nessun servizio approvato disponibile trovato.').classes(
                        "text-grey-7 q-mt-md").style("text-align:center;font-size:1.12em;")
                return
            for servizio in filtered:
                with servizi_approvati_container:
                    ui.label(f"{servizio.tipo} (Codice: {servizio.codiceServizio})").classes('text-h6 q-mb-sm')
                    ui.button('Visualizza dettagli', icon='visibility', on_click=lambda s=servizio: ui.navigate.to(f'/servizio_dettagli/{s.id}')).classes('q-pa-md')
                    ui.button('Documentazione', icon='folder', on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti')).classes('q-pa-md')

        carica_tutti_servizi()
        refresh_servizi()
        refresh_servizi_altri()
        refresh_servizi_approvati_disponibili()

        def on_search_change(e):
            refresh_servizi(search_box.value)
            refresh_servizi_altri(search_box.value)
            refresh_servizi_approvati_disponibili(search_box.value)

        search_box.on('update:model-value', on_search_change)

    crea_servizio_dialog = ui.dialog()
    with crea_servizio_dialog:
        with ui.card().classes('q-pa-md').style('max-width:400px;'):
            ui.label('Crea nuovo servizio').classes('text-h6 q-mb-md')
            cliente_id_input = ui.input('ID Cliente').props('outlined dense type=number').classes('q-mb-sm')
            tipo_input = ui.select(TIPI_SERVIZIO, label="Tipo servizio").props("outlined dense").classes("q-mb-sm")
            codice_corrente_input = ui.input('Codice corrente').props('outlined dense').classes('q-mb-sm')
            codice_servizio_input = ui.input('Codice servizio').props('outlined dense').classes('q-mb-sm')
            msg_crea = ui.label().classes('text-negative q-mb-sm')

            def submit_servizio():
                if not cliente_id_input.value or not tipo_input.value or not codice_corrente_input.value or not codice_servizio_input.value:
                    msg_crea.text = 'Compila tutti i campi!'
                    return
                try:
                    api_session.crea_servizio(
                        int(cliente_id_input.value), tipo_input.value, codice_corrente_input.value, codice_servizio_input.value,
                        dipendente_id=dipendente_id
                    )
                    ui.notify('Servizio creato!', color='positive')
                    crea_servizio_dialog.close()
                    carica_tutti_servizi()
                    refresh_servizi(search_box.value)
                    refresh_servizi_approvati_disponibili(search_box.value)
                except Exception as e:
                    msg_crea.text = f'Errore: {e}'

            ui.button('Crea', on_click=submit_servizio).classes('q-mt-md q-pa-md')
            ui.button('Annulla', on_click=lambda: crea_servizio_dialog.close()).classes('q-ml-md q-pa-md')