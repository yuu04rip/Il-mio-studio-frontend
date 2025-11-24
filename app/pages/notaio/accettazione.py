from nicegui import ui
from app.api.api import api_session

TIPI_SERVIZIO = {
    'atto': 'Atto',
    'compromesso': 'Compromesso',
    'preventivo': 'Preventivo',
}


def accettazione_notaio_page():
    ui.label('Gestione Servizi (Notaio) - Accettazione').classes(
        'text-h5 q-mt-xl q-mb-lg'
    ).style(
        'background:#1976d2;color:white;border-radius:2em;'
        'padding:.5em 2.5em;display:block;text-align:center;'
        'font-weight:600;letter-spacing:0.04em;'
    )

    servizi_container = ui.column().classes('full-width').style('gap:24px;')

    def stato(servizio: dict) -> str:
        """Normalizza lo stato in minuscolo."""
        return str(servizio.get('statoServizio', '')).strip().lower()

    def update_servizi():
        servizi_container.clear()
        try:
            resp = api_session.get('/studio/notai/servizi')
            print('[DEBUG][notaio] GET /studio/notai/servizi status:', resp.status_code)
            if resp.status_code != 200:
                print('[DEBUG][notaio] risposta non 200:', resp.text)
                ui.notify("Errore nel recupero dei servizi.", color="negative")
                return
            servizi = resp.json()
            print('[DEBUG][notaio] servizi ricevuti (raw):', servizi)
        except Exception as e:
            print('[DEBUG][notaio] errore connessione /studio/notai/servizi:', e)
            ui.notify(f"Errore connessione: {e}", color="negative")
            return

        da_revisionare = [s for s in servizi if stato(s) == 'in_attesa_approvazione']
        print('[DEBUG][notaio] servizi in_attesa_approvazione (count):', len(da_revisionare))

        with servizi_container:
            ui.label('Servizi da revisionare').classes('text-h6 q-mb-sm')
            if not da_revisionare:
                ui.label('Nessun servizio da revisionare.').classes('text-grey-7 q-mb-md')
                return

            for servizio in da_revisionare:
                print(
                    '[DEBUG][notaio] render servizio (da revisionare) id=',
                    servizio.get('id'),
                    'clienteNome=', servizio.get('clienteNome'),
                    'clienteCognome=', servizio.get('clienteCognome'),
                    'cliente_id=', servizio.get('cliente_id'),
                )

                tipo = servizio.get('tipo', '')
                codice = servizio.get('codiceServizio') or servizio.get('codice_servizio') or 'N/A'
                stato_label = servizio.get('statoServizio', '')

                cliente_nome = servizio.get('clienteNome') or ''
                cliente_cognome = servizio.get('clienteCognome') or ''
                cliente_display = (cliente_nome + ' ' + cliente_cognome).strip() or \
                                  f'Cliente #{servizio.get("cliente_id")}'

                with ui.card().style(
                        'background:#e3f2fd;border-radius:1em;min-height:78px;padding:1em 2em;'
                ):
                    ui.label(
                        f"{tipo} - {codice} | Stato: {stato_label}"
                    ).classes('text-body1 q-mb-xs')
                    ui.label(
                        f"Cliente: {cliente_display}"
                    ).classes('text-caption text-grey-7 q-mb-sm')

                    with ui.row().style('gap:8px;'):
                        ui.button(
                            'Accetta',
                            icon='check',
                            color='positive',
                            on_click=lambda id=servizio['id']: accetta_servizio(id),
                        ).props('flat round type="button"')
                        ui.button(
                            'Rifiuta',
                            icon='close',
                            color='negative',
                            on_click=lambda id=servizio['id']: rifiuta_servizio(id),
                        ).props('flat round type="button"')
                        ui.button(
                            'Documenti',
                            icon='folder',
                            color='accent',
                            on_click=lambda id=servizio['id']: visualizza_documenti(id),
                        ).props('flat round type="button"')

    # --- Azioni notaio ---
    def accetta_servizio(servizio_id: int):
        try:
            print('[DEBUG][notaio] accetta_servizio id=', servizio_id)
            resp = api_session.post(f'/studio/servizi/{servizio_id}/approva')
            print('[DEBUG][notaio] POST /studio/servizi/{id}/approva status:',
                  resp.status_code, resp.text)
            if resp.status_code == 200:
                ui.notify('Servizio accettato!', color='positive')
                update_servizi()
            else:
                ui.notify('Errore accettazione servizio', color='negative')
        except Exception as e:
            print('[DEBUG][notaio] errore accetta_servizio:', e)
            ui.notify(f'Errore connessione: {e}', color='negative')

    def rifiuta_servizio(servizio_id: int):
        try:
            print('[DEBUG][notaio] rifiuta_servizio id=', servizio_id)
            resp = api_session.post(f'/studio/servizi/{servizio_id}/rifiuta')
            print('[DEBUG][notaio] POST /studio/servizi/{id}/rifiuta status:',
                  resp.status_code, resp.text)
            if resp.status_code == 200:
                ui.notify('Servizio rifiutato!', color='positive')
                update_servizi()
            else:
                ui.notify('Errore rifiuto servizio', color='negative')
        except Exception as e:
            print('[DEBUG][notaio] errore rifiuta_servizio:', e)
            ui.notify(f'Errore connessione: {e}', color='negative')

    def visualizza_documenti(servizio_id: int):
        print('[DEBUG][notaio] visualizza_documenti servizio_id=', servizio_id)
        ui.navigate.to(f'/servizi/{servizio_id}/documenti')

    update_servizi()