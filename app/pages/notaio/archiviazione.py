from nicegui import ui
from app.api.api import api_session

TIPI_SERVIZIO = {
    'atto': 'Atto',
    'compromesso': 'Compromesso',
    'preventivo': 'Preventivo',
}


def servizi_notaio_archiviati_page():
  with ui.card().classes(
    'q-mx-auto q-my-xl shadow-3'
).style(
    'width: 900px;'
    'background: rgba(240,240,240) !important;'
    'box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important;'
    'border-radius: 2.5em !important;'
    'border: 1.7px solid #e3eaf1 !important;'
    'backdrop-filter: blur(6px);'
    'align-items:center;'
):
   with ui.row().classes('items-center q-mb-md').style('align-items:center; gap:40px; justify-content:center;'):
    ui.icon('archive', size='40px').classes('q-mr-md').style('color:#1976d2')
    ui.label('SERVIZI ARCHIVIATI').classes(
        'text-h5 q-mt-xl q-mb-lg'
    ).style(
        'font-weight:600;font-size:2rem;color: #1976d2;letter-spacing: 0.5px;margin: 0;padding: 0;background: none;box-shadow: none;'
    )

    servizi_container = ui.column().classes('full-width').style('gap:18px;')

    def update_servizi():
        servizi_container.clear()
        try:
            resp = api_session.get('/studio/notai/servizi')
            print('[DEBUG][notaio-archiviati] GET /studio/notai/servizi status:', resp.status_code)
            if resp.status_code != 200:
                print('[DEBUG][notaio-archiviati] risposta non 200:', resp.text)
                ui.notify("Errore nel recupero dei servizi.", color="negative")
                return
            servizi = resp.json()
            print('[DEBUG][notaio-archiviati] servizi ricevuti (raw):', servizi)
        except Exception as e:
            print('[DEBUG][notaio-archiviati] errore connessione /studio/notai/servizi:', e)
            ui.notify(f"Errore connessione: {e}", color="negative")
            return

        archiviati = [s for s in servizi if s.get('archived', False)]
        print('[DEBUG][notaio-archiviati] servizi archiviati (count):', len(archiviati))

        with servizi_container:
            if not archiviati:
                ui.label('Nessun servizio archiviato.').classes('text-grey-7 q-mb-md')
                return

            for servizio in archiviati:
                print('[DEBUG][notaio-archiviati] render servizio (archiviato) id=', servizio.get('id'))
                tipo = servizio.get('tipo', '')
                codice = servizio.get('codiceServizio') or servizio.get('codice_servizio') or 'N/A'
                stato_label = servizio.get('statoServizio', '')

                cliente_nome = servizio.get('clienteNome') or ''
                cliente_cognome = servizio.get('clienteCognome') or ''
                cliente_display = (cliente_nome + ' ' + cliente_cognome).strip() or \
                                  f'Cliente #{servizio.get("cliente_id")}'

                with ui.card().style(
                        'background:#f5fcf4;border-radius:1em;min-height:72px;padding:1em 2em;width:100%;'
                ):
                    ui.label(
                        f"{tipo} - {codice} | Stato: {stato_label}"
                    ).classes('text-h6 q-mb-sm')
                    ui.label(
                        f"Cliente: {cliente_display}"
                    ).classes('text-caption text-grey-7 q-mb-sm')
                    with ui.row().style('gap:16px;'):
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
                                print('[DEBUG][notaio-archiviati] dearchivia_servizio id=', sid)
                                api_session.dearchivia_servizio(sid)
                                ui.notify("Servizio dearchiviato!", color="positive")
                            except Exception as e:
                                ui.notify(f"Errore dearchiviazione: {e}", color="negative")
                                print('[DEBUG][notaio-archiviati] errore dearchivia_servizio:', e)
                            finally:
                                update_servizi()

                        ui.button(
                            'Dearchivia',
                            icon='unarchive',
                            color='secondary',
                            on_click=lambda sid=servizio['id']: dearchivia_and_refresh(sid),
                        ).props('flat round type="button"')

    def visualizza_documenti(servizio_id: int):
        print('[DEBUG][notaio-archiviati] visualizza_documenti servizio_id=', servizio_id)
        ui.navigate.to(f'/servizi/{servizio_id}/documenti')

    def visualizza_dettagli(servizio_id: int):
        print('[DEBUG][notaio-archiviati] visualizza_dettagli servizio_id=', servizio_id)
        ui.navigate.to(f'/servizi_notaio/{servizio_id}/dettagli')

    update_servizi()