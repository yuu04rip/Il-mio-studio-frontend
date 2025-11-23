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
        'background:#1976d2;color:white;border-radius:2em;padding:.5em 2.5em;'
        'display:block;text-align:center;font-weight:600;letter-spacing:0.04em;'
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

        # DEBUG: logga flags archiviazione / eliminazione per ogni servizio
        for s in servizi:
            print(
                '[DEBUG][notaio] servizio id=', s.get('id'),
                'statoServizio=', s.get('statoServizio'),
                'archived=', s.get('archived'),
                'is_deleted=', s.get('is_deleted'),
            )

        da_revisionare = [s for s in servizi if stato(s) == 'in_attesa_approvazione']
        archiviati = [s for s in servizi if s.get('archived', False)]

        print('[DEBUG][notaio] servizi in_attesa_approvazione (count):', len(da_revisionare))
        print('[DEBUG][notaio] servizi archiviati (count):', len(archiviati))

        with servizi_container:
            # --- Sezione: Da revisionare ---
            ui.label('Servizi da revisionare').classes('text-h6 q-mb-sm')
            if not da_revisionare:
                ui.label('Nessun servizio da revisionare.').classes('text-grey-7 q-mb-md')
            else:
                for servizio in da_revisionare:
                    print('[DEBUG][notaio] render servizio (da revisionare) id=', servizio.get('id'),
                          'clienteNome=', servizio.get('clienteNome'),
                          'clienteCognome=', servizio.get('clienteCognome'),
                          'cliente_id=', servizio.get('cliente_id'))

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

            ui.separator().classes('q-my-md')

            # --- Sezione: Servizi archiviati ---
            ui.label('Servizi archiviati').classes('text-h6 q-mb-sm')
            if not archiviati:
                ui.label('Nessun servizio archiviato.').classes('text-grey-7 q-mb-md')
            else:
                for servizio in archiviati:
                    print('[DEBUG][notaio] render servizio (archiviato) id=', servizio.get('id'))
                    tipo = servizio.get('tipo', '')
                    codice = servizio.get('codiceServizio') or servizio.get('codice_servizio') or 'N/A'
                    stato_label = servizio.get('statoServizio', '')

                    cliente_nome = servizio.get('clienteNome') or ''
                    cliente_cognome = servizio.get('clienteCognome') or ''
                    cliente_display = (cliente_nome + ' ' + cliente_cognome).strip() or \
                                      f'Cliente #{servizio.get("cliente_id")}'

                    with ui.card().style(
                            'background:#f5fcf4;border-radius:1em;min-height:72px;padding:1em 2em;'
                    ):
                        ui.label(
                            f"{tipo} - {codice} | Stato: {stato_label}"
                        ).classes('text-body1 q-mb-xs')
                        ui.label(
                            f"Cliente: {cliente_display}"
                        ).classes('text-caption text-grey-7 q-mb-sm')
                        with ui.row().style('gap:8px;'):
                            ui.button(
                                'Dettagli',
                                icon='visibility',
                                color='primary',
                                on_click=lambda id=servizio['id']: visualizza_dettagli(id),
                            ).props('flat round type="button"')
                            ui.button(
                                'Documenti',
                                icon='folder',
                                color='accent',
                                on_click=lambda id=servizio['id']: visualizza_documenti(id),
                            ).props('flat round type="button"')

                            # Bottone Dearchivia (ripristina il servizio tra quelli attivi)
                            def dearchivia_and_refresh(sid=servizio['id']):
                                try:
                                    print('[DEBUG][notaio] dearchivia_servizio id=', sid)
                                    api_session.dearchivia_servizio(sid)
                                    ui.notify("Servizio dearchiviato!", color="positive")
                                except Exception as e:
                                    ui.notify(f"Errore dearchiviazione: {e}", color="negative")
                                    print('[DEBUG][notaio] errore dearchivia_servizio:', e)
                                finally:
                                    update_servizi()

                            ui.button(
                                'Dearchivia',
                                icon='unarchive',
                                color='secondary',
                                on_click=lambda sid=servizio['id']: dearchivia_and_refresh(sid),
                            ).props('flat round type="button"')

    # --- Azioni notaio ---
    def accetta_servizio(servizio_id: int):
        try:
            print('[DEBUG][notaio] accetta_servizio id=', servizio_id)
            resp = api_session.post(f'/studio/servizi/{servizio_id}/approva')
            print('[DEBUG][notaio] POST /studio/servizi/{id}/approva status:', resp.status_code, resp.text)
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
            print('[DEBUG][notaio] POST /studio/servizi/{id}/rifiuta status:', resp.status_code, resp.text)
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

    def visualizza_dettagli(servizio_id: int):
        print('[DEBUG][notaio] visualizza_dettagli servizio_id=', servizio_id)
        ui.navigate.to(f'/servizi_notaio/{servizio_id}/dettagli')

    update_servizi()