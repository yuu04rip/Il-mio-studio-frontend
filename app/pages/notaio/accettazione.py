from nicegui import ui
from app.api.api import api_session

TIPI_SERVIZIO = {
    'atto': 'Atto',
    'compromesso': 'Compromesso',
    'preventivo': 'Preventivo',
}

def accettazione_notaio_page():
    ui.label('Gestione Servizi (Notaio)').classes(
        'text-h5 q-mt-xl q-mb-lg'
    ).style(
        'background:#1976d2;color:white;border-radius:2em;padding:.5em 2.5em;display:block;text-align:center;font-weight:600;letter-spacing:0.04em;'
    )

    current_tab = {'value': 'Da revisionare'}

    tab_row = ui.row().classes('q-mb-lg q-mt-md')
    with tab_row:
        btn_da_revisionare = ui.button(
            'Da revisionare',
            on_click=lambda: (current_tab.update({'value': 'Da revisionare'}), update_servizi()),
            color='primary'
        )
        btn_revisionati = ui.button(
            'Revisionati',
            on_click=lambda: (current_tab.update({'value': 'Revisionati'}), update_servizi()),
            color='default'
        )

    servizi_container = ui.column().classes('full-width').style('gap:18px;')

    aggiungi_servizio_dialog = ui.dialog()
    with aggiungi_servizio_dialog:
        with ui.card().classes('q-pa-md').style('max-width:400px;'):
            ui.label('Aggiungi Servizio (Approvato)').classes('text-h6 q-mb-md')
            cliente_id_input = ui.input('ID Cliente').props('outlined dense type=number').classes('q-mb-sm')
            tipo_input = ui.select(TIPI_SERVIZIO, label="Tipo servizio").props("outlined dense").classes("q-mb-sm")
            codice_corrente_input = ui.input('Codice corrente').props('outlined dense').classes('q-mb-sm')
            # rimosso input codice_servizio_input: il codice ufficiale viene generato dal backend
            msg_crea = ui.label().classes('text-negative q-mb-sm')
            user = api_session.user
            dipendente_id = api_session.get_dipendente_id_by_user(user['id']) if user else None

            def submit_servizio():
                # validazioni di base
                if not (cliente_id_input.value and tipo_input.value and codice_corrente_input.value):
                    msg_crea.text = 'Compila tutti i campi!'
                    return
                try:
                    # assicurati che codiceCorrente sia intero
                    try:
                        codice_corrente_val = int(codice_corrente_input.value)
                    except Exception:
                        msg_crea.text = 'Codice corrente deve essere un numero intero'
                        return

                    payload = {
                        "cliente_id": int(cliente_id_input.value),
                        "tipo": tipo_input.value,
                        "codiceCorrente": int(codice_corrente_val),
                        "dipendente_id": dipendente_id
                    }
                    # invia la creazione senza codiceServizio: il backend lo genera automaticamente
                    resp = api_session.post('/studio/servizi', json=payload)
                    if resp.status_code == 200:
                        servizio = resp.json()
                        servizio_id = servizio.get("id")
                        codice_generato = servizio.get("codiceServizio") or servizio.get("codice_servizio")
                        # imposta lo stato APPROVATO
                        patch_resp = api_session.patch(
                            f"/studio/servizi/{servizio_id}",
                            {"statoServizio": "APPROVATO"}
                        )
                        if patch_resp.status_code == 200:
                            if codice_generato:
                                ui.notify(f'Servizio creato e approvato! Codice: {codice_generato}', color='positive')
                            else:
                                ui.notify('Servizio creato e approvato!', color='positive')
                            aggiungi_servizio_dialog.close()
                            update_servizi()
                        else:
                            msg_crea.text = f"Servizio creato ma errore nella modifica stato: {patch_resp.text}"
                    else:
                        msg_crea.text = f"Errore: {resp.text}"
                except Exception as e:
                    msg_crea.text = f'Errore: {e}'

            ui.button('Crea', on_click=submit_servizio).props('type="button"').classes('q-mt-md q-pa-md')
            ui.button('Annulla', on_click=lambda: aggiungi_servizio_dialog.close()).props('type="button"').classes('q-ml-md q-pa-md')

    def stato(servizio):
        return str(servizio.get('statoServizio', '')).strip().lower()

    def update_servizi():
        btn_da_revisionare.props('color="primary"' if current_tab['value'] == 'Da revisionare' else 'color="default"')
        btn_revisionati.props('color="primary"' if current_tab['value'] == 'Revisionati' else 'color="default"')
        servizi_container.clear()
        try:
            resp = api_session.get('/studio/notai/servizi')
            if resp.status_code != 200:
                ui.notify("Errore nel recupero dei servizi.", color="negative")
                return
            servizi = resp.json()
        except Exception as e:
            ui.notify(f"Errore connessione: {e}", color="negative")
            return

        with servizi_container:
            if current_tab['value'] == 'Da revisionare':
                da_revisionare = [s for s in servizi if stato(s) == 'in_attesa_approvazione']
                if not da_revisionare:
                    ui.label('Nessun servizio da revisionare.').classes('text-grey-7 q-mt-md')
                for servizio in da_revisionare:
                    with ui.card().style('background:#e3f2fd;border-radius:1em;min-height:78px;padding:1em 2em;'):
                        ui.label(
                            f"{servizio['tipo']} - {servizio['codiceServizio']} | Stato: {servizio.get('statoServizio','')}"
                        ).classes('text-body1 q-mb-xs')
                        with ui.row().style('gap:8px;'):
                            ui.button('Accetta', icon='check', color='positive',
                                      on_click=lambda id=servizio['id']: accetta_servizio(id)).props('flat round type="button"')
                            ui.button('Rifiuta', icon='close', color='negative',
                                      on_click=lambda id=servizio['id']: rifiuta_servizio(id)).props('flat round type="button"')
                            ui.button('Documenti', icon='folder', color='accent',
                                      on_click=lambda id=servizio['id']: visualizza_documenti(id)).props('flat round type="button"')
            else:
                ui.button(
                    'Aggiungi Servizio',
                    icon='add',
                    color='info',
                    on_click=lambda: aggiungi_servizio_dialog.open()
                ).props('type="button"').classes('q-mb-lg q-pa-md')

                revisionati = [s for s in servizi if stato(s) in ('approvato', 'rifiutato')]
                if not revisionati:
                    ui.label('Nessun servizio revisionato.').classes('text-grey-7 q-mt-md')
                for servizio in revisionati:
                    with ui.card().style('background:#f5fcf4;border-radius:1em;min-height:78px;padding:1em 2em;'):
                        ui.label(
                            f"{servizio['tipo']} - {servizio['codiceServizio']} | Stato: {servizio.get('statoServizio','')}"
                        ).classes('text-body1 q-mb-xs')
                        with ui.row().style('gap:8px;'):
                            ui.button('Documenti', icon='folder', color='accent',
                                      on_click=lambda id=servizio['id']: visualizza_documenti(id)).props('flat round type="button"')
                            ui.button('Dettagli', icon='info', color='primary',
                                      on_click=lambda id=servizio['id']: visualizza_dettagli(id)).props('flat round type="button"')

    def accetta_servizio(servizio_id):
        try:
            resp = api_session.post(f'/studio/servizi/{servizio_id}/approva')
            if resp.status_code == 200:
                ui.notify('Servizio accettato!', color='positive')
                update_servizi()
            else:
                ui.notify('Errore accettazione servizio', color='negative')
        except Exception as e:
            ui.notify(f'Errore connessione: {e}', color='negative')

    def rifiuta_servizio(servizio_id):
        try:
            resp = api_session.post(f'/studio/servizi/{servizio_id}/rifiuta')
            if resp.status_code == 200:
                ui.notify('Servizio rifiutato!', color='positive')
                update_servizi()
            else:
                ui.notify('Errore rifiuto servizio', color='negative')
        except Exception as e:
            ui.notify(f'Errore connessione: {e}', color='negative')

    def visualizza_documenti(servizio_id):
        ui.navigate.to(f'/servizi/{servizio_id}/documenti')

    def visualizza_dettagli(servizio_id):
        ui.navigate.to(f'/servizi_notaio/{servizio_id}/dettagli')

    update_servizi()