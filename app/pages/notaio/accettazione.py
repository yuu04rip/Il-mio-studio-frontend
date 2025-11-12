from nicegui import ui
from app.api.api import api_session

TIPI_SERVIZIO = {
    'atto': 'Atto',
    'compromesso': 'Compromesso',
    'preventivo': 'Preventivo',
}

def accettazione_notaio_page():
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
    with ui.card().classes('q-mb-xl shadow-3').style('background: rgba(240,240,240) !important;box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important;border-radius: 2.5em !important;border: 1.7px solid #e3eaf1 !important;backdrop-filter: blur(6px);-webkit-backdrop-filter: blur(6px);overflow: hidden;margin: auto;align-items:center;max-width: 600px;width: 100%;'):
        ui.label('Gestione Servizi ').classes(
            'text-h5 q-mt-xl q-mb-lg'
        ).style(
            'background: trasporant !importtant;color:#1976d2;border-radius:2em;padding:.6em 2.5em;display:block;text-align:center;font-weight:600;letter-spacing:0.04em;font-size:2rem;'
        )

        current_tab = {'value': 'Da revisionare'}

        tab_row = ui.row().classes('justify-center items-center no-wrap gap-4')
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
            with ui.card().classes('q-pa-md').style('max-width:400px;width:100%; align-items:center;'):
                ui.label('Aggiungi Servizio (Approvato)').classes('text-h6 q-mb-md').style('color: #1976d2')
                cliente_id_input = ui.input('ID Cliente').props('outlined dense type=number').classes('q-mb-sm').style("min-width:200px; max-width:300px;width:100%;")
                tipo_input = ui.select(TIPI_SERVIZIO, label="Tipo servizio").props("outlined dense").classes("q-mb-sm").style("min-width:200px; max-width:300px;width:100%;")
                codice_corrente_input = ui.input('Codice corrente').props('outlined dense').classes('q-mb-sm').style("min-width:200px; max-width:300px;width:100%;")
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

                ui.button('Crea', on_click=submit_servizio).props('type="button"').classes('custom-button-blue-light-panels')
                ui.button('Annulla', on_click=lambda: aggiungi_servizio_dialog.close()).props('type="button"').classes('custom-button-blue-light-panels')

        def stato(servizio):
            return str(servizio.get('statoServizio', '')).strip().lower()

        def update_servizi():
            ui.add_head_html("""
<style>
.custom-btn.q-btn{
    font-size: 1.12em !important;
    font-weight: 600;
    border-radius: 1.8em !important;
    background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px 0 #2196f341;
    padding: 0.95em 0 !important;
    margin-top: 10px;
    transition: background .17s, box-shadow .16s, transform .14s;
    border: none !important;
    max-width:150px;
    width:100%;
    flex:none;
}
.custom-btn-nowidth.q-btn {
    font-size: 1.12em !important;
    font-weight: 600;
    border-radius: 1.8em !important;
    background: rgba(240, 240, 240, 1) !important;
    color: #000 !important;
    box-shadow: 0 4px 16px 0 #00000011;
    padding: 0.95em 0 !important;
    margin-top: 10px;
    transition: background .17s, box-shadow .16s, transform .14s;
    border: 1.5px solid #e0e0e0 !important;
    max-width:150px;
    width:100%;
    flex:none;
}
</style>
""")
            btn_da_revisionare.classes(
                add='custom-btn' if current_tab['value'] == 'Da revisionare' else 'custom-btn-nowidth',
                remove='custom-btn-nowidth' if current_tab['value'] == 'Da revisionare' else 'custom-btn'
            )

            btn_revisionati.classes(
                add='custom-btn' if current_tab['value'] == 'Revisionati' else 'custom-btn-nowidth',
                remove='custom-btn-nowidth' if current_tab['value'] == 'Revisionati' else 'custom-btn'
            )
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
                        with ui.card().style('background:#e3f2fd;border-radius:1em;min-height:78px;padding:1em 2em;max-width:600px;width:100%;'):
                            ui.label(
                                f"{servizio['tipo']} - {servizio['codiceServizio']} | Stato: {servizio.get('statoServizio','')}"
                            ).classes('text-body1 q-mb-xs').style('font-weight: bold;')
                            with ui.row().style('gap:8px;'):
                                ui.button('Accetta', icon='check', color='positive',
                                        on_click=lambda id=servizio['id']: accetta_servizio(id)).props('flat round type="button"')
                                ui.button('Rifiuta', icon='close', color='negative',
                                        on_click=lambda id=servizio['id']: rifiuta_servizio(id)).props('flat round type="button"')
                                ui.button('Documenti', icon='folder', color='accent',
                                        on_click=lambda id=servizio['id']: visualizza_documenti(id)).props('flat round type="button"')
                else:
                    ui.button(
                        icon='add',
                        on_click=lambda: aggiungi_servizio_dialog.open()
                    ).props('type="button"').classes('custom-btn').style(
                        'display:block; margin:0 auto;'
                    )

                    revisionati = [s for s in servizi if stato(s) in ('approvato', 'rifiutato')]
                    if not revisionati:
                        ui.label('Nessun servizio revisionato.').classes('text-grey-7 q-mt-md')
                    for servizio in revisionati:
                        with ui.card().style('background:#f5fcf4;border-radius:1em;min-height:78px;padding:1em 2em;max-width:600px;width:100%;'):
                            ui.label(
                                f"{servizio['tipo']} - {servizio['codiceServizio']} | Stato: {servizio.get('statoServizio','')}"
                            ).classes('text-body1 q-mb-xs').style('font-weight: bold;')
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