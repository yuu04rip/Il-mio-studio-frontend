from nicegui import ui
from app.api.api import api_session
from app.models.servizio import Servizio  # Assicurati che il model abbia il campo 'stato'

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
    dipendente_id = user.get('id') if user else None
    if not dipendente_id:
        ui.label("Utente non autenticato").classes('text-negative q-mt-xl')
        return

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        # Barra superiore
        with ui.row().classes('items-center q-mb-md'):
            ui.icon('engineering', size='40px').classes('q-mr-md')
            ui.label('SERVIZI DA SVOLGERE').classes(
                'text-h5').style('background:#1a237e;color:white;border-radius:2em;padding:.5em 2em;')
            search_box = ui.input('', placeholder="Cerca servizio...").props(
                'dense').classes('q-ml-md').style('max-width:200px;')
            # Bottone per aprire il dialog di creazione servizio
            ui.button('Crea Servizio', icon='add',
                      on_click=lambda: crea_servizio_dialog.open()).classes('q-ml-lg q-pa-md')

        servizi = []
        # Recupera i servizi assegnati al dipendente
        res = api_session.visualizza_lavoro_da_svolgere(dipendente_id)
        if isinstance(res, list):
            servizi = [Servizio.from_dict(s) for s in res]
        else:
            ui.label("Errore nel recupero dei servizi.").classes("text-negative q-mt-lg")

        servizi_container = ui.column().classes('full-width').style('gap:18px;')

        def refresh_servizi(filter_text=""):
            servizi_container.clear()
            filtered = servizi
            if filter_text:
                filtered = [s for s in servizi if filter_text.lower() in s.tipo.lower()
                            or filter_text.lower() in str(s.codiceServizio)]
            if not filtered:
                with servizi_container:
                    ui.label('Nessun servizio trovato.').classes(
                        "text-grey-7 q-mt-md").style("text-align:center;font-size:1.12em;")
            for servizio in filtered:
                if getattr(servizio, "is_deleted", False):
                    continue
                with servizi_container:
                    with ui.card().classes('q-pa-md q-mb-md').style('background:#e0f7fa'):
                        ui.label(
                            f"{servizio.tipo} (Codice: {servizio.codiceServizio})"
                        ).classes('text-h6 q-mb-sm')
                        with ui.row().classes('items-center q-gutter-xs'):
                            ui.icon(get_icon_for_stato(str(servizio.stato)), size='24px').classes('q-mr-xs')
                            ui.label(
                                f"Stato: {servizio.stato}").classes('text-subtitle2 q-mb-xs')
                        with ui.row().classes('q-gutter-md'):
                            # INIZIALIZZA (se stato == CREATO)
                            if str(servizio.stato) == 'CREATO':
                                ui.button(
                                    'Inizializza', icon='play_arrow',
                                    on_click=lambda s=servizio: inizializza_servizio(s.id)
                                ).classes('q-pa-md')
                            # CARICA DOCUMENTO (se stato == IN_LAVORAZIONE)
                            if str(servizio.stato) == 'IN_LAVORAZIONE':
                                ui.button(
                                    'Carica documento', icon='upload',
                                    on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/carica')
                                ).classes('q-pa-md')
                                ui.button(
                                    'Inoltra al notaio', icon='send',
                                    on_click=lambda s=servizio: inoltra_servizio_notaio(s.id)
                                ).classes('q-pa-md')
                            # Visualizza documentazione sempre
                            ui.button(
                                'Documentazione', icon='folder',
                                on_click=lambda s=servizio: ui.navigate.to(f'/servizi/{s.id}/documenti')
                            ).classes('q-pa-md')

        def inizializza_servizio(servizio_id):
            try:
                resp = api_session.inizializza_servizio(servizio_id)
                ui.notify("Servizio inizializzato!", color="positive")
                servizi[:] = [Servizio.from_dict(s) for s in api_session.visualizza_lavoro_da_svolgere(dipendente_id)]
                refresh_servizi(search_box.value)
            except Exception as e:
                ui.notify(str(e), color="negative")

        def inoltra_servizio_notaio(servizio_id):
            try:
                resp = api_session.inoltra_servizio_notaio(servizio_id)
                ui.notify("Servizio inoltrato al notaio!", color="positive")
                servizi[:] = [Servizio.from_dict(s) for s in api_session.visualizza_lavoro_da_svolgere(dipendente_id)]
                refresh_servizi(search_box.value)
            except Exception as e:
                ui.notify(str(e), color="negative")

        def on_search_change(e):
            refresh_servizi(search_box.value)

        search_box.on('update:model-value', on_search_change)

        refresh_servizi()

    # --- DIALOG per creazione servizio ---
    crea_servizio_dialog = ui.dialog()
    with crea_servizio_dialog:
        with ui.card().classes('q-pa-md').style('max-width:400px;'):
            ui.label('Crea nuovo servizio').classes('text-h6 q-mb-md')
            cliente_id_input = ui.input('ID Cliente').props(
                'outlined dense type=number').classes('q-mb-sm')
            tipo_input = ui.select(TIPI_SERVIZIO, label="Tipo servizio").props(
                "outlined dense").classes("q-mb-sm")
            codice_corrente_input = ui.input('Codice corrente').props(
                'outlined dense').classes('q-mb-sm')
            codice_servizio_input = ui.input('Codice servizio').props(
                'outlined dense').classes('q-mb-sm')
            msg_crea = ui.label().classes('text-negative q-mb-sm')

            def submit_servizio():
                cliente_id = cliente_id_input.value
                tipo = tipo_input.value
                codice_corrente = codice_corrente_input.value
                codice_servizio = codice_servizio_input.value
                if not cliente_id or not tipo or not codice_corrente or not codice_servizio:
                    msg_crea.text = 'Compila tutti i campi!'
                    return
                try:
                    # MODIFICA: passa anche il dipendente_id!
                    resp = api_session.crea_servizio(
                        int(cliente_id), tipo, codice_corrente, codice_servizio, dipendente_id=dipendente_id
                    )
                    ui.notify('Servizio creato!', color='positive')
                    crea_servizio_dialog.close()
                    servizi[:] = [Servizio.from_dict(s) for s in api_session.visualizza_lavoro_da_svolgere(dipendente_id)]
                    refresh_servizi(search_box.value)
                except Exception as e:
                    msg_crea.text = f'Errore: {e}'

            ui.button('Crea', on_click=submit_servizio).classes('q-mt-md q-pa-md')
            ui.button('Annulla', on_click=lambda: crea_servizio_dialog.close()).classes('q-ml-md q-pa-md')