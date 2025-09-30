from nicegui import ui
from app.api.api import api_session
from app.models.servizio import Servizio

def servizio_cliente_dettagli_page(cliente_id: int, servizio_id: int):
    """Pagina dettagli servizio per il cliente"""

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto').style('max-width: 800px;'):
        # Header
        with ui.row().classes('items-center q-mb-lg'):
            ui.button(
                icon='arrow_back',
                on_click=lambda: ui.navigate.to(f'/servizi_cliente/{cliente_id}')
            ).classes('q-mr-md')
            ui.label('DETTAGLI SERVIZIO').classes('text-h4 text-weight-bold')

        try:
            servizio_data = api_session.get(f'/studio/servizi/{servizio_id}')
            servizio_data.raise_for_status()
            servizio = Servizio.from_dict(servizio_data.json())

            cliente_data = api_session.get(f'/studio/clienti/{servizio.cliente_id}/dettagli')
            cliente_data.raise_for_status()
            cliente = cliente_data.json()
        except Exception as e:
            ui.notify(f"Errore nel caricamento dei dettagli: {e}", color="negative")
            ui.label("Impossibile caricare i dettagli del servizio").classes('text-negative q-mt-md')
            return

        # Info principali
        with ui.card().classes('q-pa-md q-mb-md').style('background:#f5f5f5;'):
            ui.label('INFORMAZIONI PRINCIPALI').classes('text-h6 text-weight-bold q-mb-md')
            with ui.grid(columns=2).classes('w-full gap-4'):
                with ui.column():
                    ui.label('Tipo Servizio:').classes('text-weight-bold')
                    ui.label(servizio.tipo.value if hasattr(servizio.tipo, 'value') else servizio.tipo).classes('text-body1')
                    ui.label('Codice Servizio:').classes('text-weight-bold q-mt-md')
                    ui.label(str(servizio.codiceServizio)).classes('text-body1')
                    ui.label('Stato:').classes('text-weight-bold q-mt-md')
                    with ui.row().classes('items-center'):
                        icon_color = {
                            'CREATO': 'text-blue',
                            'IN_LAVORAZIONE': 'text-orange',
                            'IN_ATTESA_APPROVAZIONE': 'text-yellow',
                            'APPROVATO': 'text-green',
                            'RIFIUTATO': 'text-red',
                            'CONSEGNATO': 'text-purple'
                        }.get(servizio.statoServizio, 'text-grey')
                        ui.icon(get_icon_for_stato(servizio.statoServizio)).classes(f'{icon_color} q-mr-sm')
                        ui.label(servizio.statoServizio).classes('text-body1')
                with ui.column():
                    ui.label('Codice Corrente:').classes('text-weight-bold')
                    ui.label(str(servizio.codiceCorrente)).classes('text-body1')
                    ui.label('Data Richiesta:').classes('text-weight-bold q-mt-md')
                    ui.label(servizio.dataRichiesta.strftime('%d/%m/%Y %H:%M') if hasattr(servizio.dataRichiesta, 'strftime') else servizio.dataRichiesta).classes('text-body1')
                    ui.label('Data Consegna:').classes('text-weight-bold q-mt-md')
                    ui.label(servizio.dataConsegna.strftime('%d/%m/%Y %H:%M') if hasattr(servizio.dataConsegna, 'strftime') else servizio.dataConsegna).classes('text-body1')

        # Info cliente
        with ui.card().classes('q-pa-md q-mb-md').style('background:#e8f5e8;'):
            ui.label('I TUOI DATI').classes('text-h6 text-weight-bold q-mb-md')
            with ui.grid(columns=2).classes('w-full gap-4'):
                with ui.column():
                    ui.label('Nome e Cognome:').classes('text-weight-bold')
                    ui.label(f"{cliente.get('nome', 'N/A')} {cliente.get('cognome', 'N/A')}").classes('text-body1')
                    ui.label('Email:').classes('text-weight-bold q-mt-md')
                    ui.label(cliente.get('email', 'N/A')).classes('text-body1')
                with ui.column():
                    ui.label('Telefono:').classes('text-weight-bold')
                    ui.label(cliente.get('numeroTelefonico', 'N/A')).classes('text-body1')
                    ui.label('ID Cliente:').classes('text-weight-bold q-mt-md')
                    ui.label(str(cliente.get('id', 'N/A'))).classes('text-body1')

        # Dipendente responsabile
        with ui.card().classes('q-pa-md q-mb-md').style('background:#e3f2fd;'):
            ui.label('REFERENTE STUDIO').classes('text-h6 text-weight-bold q-mb-md')
            try:
                dipendenti_resp = api_session.get(f'/studio/servizi/{servizio_id}/dipendenti')
                if dipendenti_resp.status_code == 200:
                    dipendenti = dipendenti_resp.json()
                    if dipendenti:
                        dip_responsabile = dipendenti[0]
                        with ui.row().classes('items-center q-pa-sm'):
                            ui.icon('person').classes('q-mr-sm')
                            ui.label(
                                f"{dip_responsabile.get('nome', 'N/A')} {dip_responsabile.get('cognome', 'N/A')} "
                                f"(ID: {dip_responsabile.get('id', 'N/A')})"
                            ).classes('text-body1')
                    else:
                        ui.label("Nessun referente assegnato").classes('text-grey-7 italic')
                else:
                    ui.label("Impossibile recuperare il referente").classes('text-grey-7 italic')
            except Exception as e:
                ui.label("Errore nel caricamento del referente").classes('text-grey-7 italic')

        # Pulsanti azione (torna alla lista col cliente_id)
        with ui.row().classes('q-mt-lg justify-center'):
            ui.button(
                'Torna alla Lista Servizi',
                icon='list',
                on_click=lambda: ui.navigate.to(f'/servizi_cliente/{cliente_id}')
            ).classes('q-pa-md')

def get_icon_for_stato(stato):
    """Funzione helper per le icone dello stato"""
    icons = {
        'CREATO': 'pending_actions',
        'IN_LAVORAZIONE': 'play_circle',
        'IN_ATTESA_APPROVAZIONE': 'hourglass_empty',
        'APPROVATO': 'check_circle',
        'RIFIUTATO': 'cancel',
        'CONSEGNATO': 'done_all',
    }
    return icons.get(stato, 'help')