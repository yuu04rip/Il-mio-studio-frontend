from nicegui import ui
from app.api.api import api_session

def servizi_cliente_approvati_page(cliente_id: int):
    """Pagina per visualizzare tutti i servizi APPROVATI di un cliente"""
    ui.button(
            'Torna alla Home',
            icon='home',
            on_click=lambda: ui.navigate.to(f'/home_cliente?cliente_id={cliente_id}')
        ).classes('q-pa-md').style(
                    'background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;color:#fff !important;'
                    'border-radius:1.8em;'
                )
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto').style('background:#f0f0f0;border-radius:2.5em;max-width: 900px;display:flex;flex-direction:column;align-items:center;justify-content:center;'):
        

        ui.label('SERVIZI APPROVATI').classes('glass-label').style(
                'color:#1976d2;text-align:center;font-size:2.5em;font-weight:bold;margin-bottom:20px;'
            )


        try:
            servizi_data = api_session.get(f'/studio/clienti/{cliente_id}/servizi_approvati')
            servizi_data.raise_for_status()
            servizi = servizi_data.json()
        except Exception as e:
            ui.notify(f"Errore nel caricamento: {e}", color="negative")
            ui.label("Impossibile caricare i servizi approvati").classes('text-negative q-mt-md').style('margin-bottom:20px;text-align:center;')
            return

        if not servizi:
            ui.label("Nessun servizio approvato trovato.").classes('text-grey-7 italic').style('margin-bottom:20px;text-align:center;')
            return

        for servizio in servizi:
            with ui.card().classes('q-pa-md q-mb-md'):
                ui.label(f"Tipo: {servizio.get('tipo', 'N/A')}").classes('text-body1')
                ui.label(f"Codice Servizio: {servizio.get('codiceServizio', 'N/A')}").classes('text-body1')
                ui.label(f"Codice Corrente: {servizio.get('codiceCorrente', 'N/A')}").classes('text-body2')
                ui.label(f"Data Richiesta: {servizio.get('dataRichiesta', 'N/A')}").classes('text-body2')
                ui.label(f"Data Consegna: {servizio.get('dataConsegna', 'N/A')}").classes('text-body2')
                ui.label(f"Stato: {servizio.get('statoServizio', 'N/A')}").classes('text-body2')
                ui.button(
                    "Vedi dettagli",
                    icon="info",
                    on_click=lambda s_id=servizio.get('id'): ui.navigate.to(f'/servizi_cliente/{cliente_id}/dettagli/{s_id}')
                ).classes("q-mt-md").style(
                    'background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;color:#fff !important;'
                    'border-radius:1.8em;'
                )