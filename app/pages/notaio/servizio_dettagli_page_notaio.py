from nicegui import ui
from app.api.api import api_session
from app.models.servizio import Servizio
from datetime import datetime
from dateutil.relativedelta import relativedelta


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


def servizio_dettagli_page_notaio(id: str = None):
    servizio_id = id
    if servizio_id is None:
        try:
            servizio_id = ui.context.page.arguments.get("id")
        except Exception:
            servizio_id = None

    if not servizio_id:
        ui.label("ID servizio non specificato").classes('text-negative q-mt-xl')
        return

    try:
        servizio_id = int(servizio_id)
    except ValueError:
        ui.label("ID servizio non valido").classes('text-negative q-mt-xl')
        return

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto').style('max-width: 800px;'):
        with ui.row().classes('items-center q-mb-lg'):
            ui.button(
                icon='arrow_back',
                on_click=lambda: ui.run_javascript('history.back()')
            ).classes('q-mr-md')
            ui.label('DETTAGLI SERVIZIO').classes('text-h4 text-weight-bold')

        try:
            servizio_resp = api_session.get(f'/studio/servizi/{servizio_id}')
            servizio_resp.raise_for_status()
            servizio_json = servizio_resp.json()
            servizio = Servizio.from_dict(servizio_json)

            cliente_data = api_session.get(f'/studio/clienti/{servizio.cliente_id}/dettagli')
            cliente_data.raise_for_status()
            cliente = cliente_data.json()

        except Exception as e:
            ui.notify(f"Errore nel caricamento dei dettagli: {e}", color="negative")
            ui.label("Impossibile caricare i dettagli del servizio").classes('text-negative q-mt-md')
            return

        # --- INFORMAZIONI PRINCIPALI ---
        with ui.card().classes('q-pa-md q-mb-md').style('background:#f5f5f5;'):
            ui.label('INFORMAZIONI PRINCIPALI').classes('text-h6 text-weight-bold q-mb-md')
            with ui.grid(columns=2).classes('w-full gap-4'):
                with ui.column():
                    ui.label('Tipo Servizio:').classes('text-weight-bold')
                    ui.label(
                        servizio.tipo.value if hasattr(servizio.tipo, 'value') else servizio.tipo
                    ).classes('text-body1')

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
                            'CONSEGNATO': 'text-purple',
                        }.get(servizio.statoServizio, 'text-grey')
                        ui.icon(get_icon_for_stato(servizio.statoServizio)).classes(
                            f'{icon_color} q-mr-sm'
                        )
                        ui.label(servizio.statoServizio).classes('text-body1')

                with ui.column():
                    ui.label('Codice Corrente:').classes('text-weight-bold')
                    ui.label(str(servizio.codiceCorrente)).classes('text-body1')

                    # Data Richiesta formattata
                    ui.label('Data Richiesta:').classes('text-weight-bold q-mt-md')
                    try:
                        if isinstance(servizio.dataRichiesta, str):
                            data_richiesta_dt = datetime.fromisoformat(servizio.dataRichiesta)
                        else:
                            data_richiesta_dt = servizio.dataRichiesta
                        data_richiesta_str = data_richiesta_dt.strftime('%d/%m/%Y %H:%M')
                    except Exception:
                        data_richiesta_str = servizio.dataRichiesta
                    ui.label(data_richiesta_str).classes('text-body1')

                    # Data Consegna +3 mesi
                    ui.label('Data Consegna:').classes('text-weight-bold q-mt-md')
                    try:
                        if isinstance(servizio.dataConsegna, str):
                            data_consegna_dt = datetime.fromisoformat(servizio.dataConsegna)
                        else:
                            data_consegna_dt = servizio.dataConsegna
                        data_consegna_plus3 = data_consegna_dt + relativedelta(months=+3)
                        data_consegna_str = data_consegna_plus3.strftime('%d/%m/%Y %H:%M')
                    except Exception:
                        data_consegna_str = servizio.dataConsegna
                    ui.label(data_consegna_str).classes('text-body1')

        # --- INFORMAZIONI CLIENTE ---
        with ui.card().classes('q-pa-md q-mb-md').style('background:#e8f5e8;'):
            ui.label('INFORMAZIONI CLIENTE').classes('text-h6 text-weight-bold q-mb-md')
            with ui.grid(columns=2).classes('w-full gap-4'):
                with ui.column():
                    ui.label('Nome e Cognome:').classes('text-weight-bold')
                    ui.label(
                        f"{cliente.get('nome', 'N/A')} {cliente.get('cognome', 'N/A')}"
                    ).classes('text-body1')

                    ui.label('Email:').classes('text-weight-bold q-mt-md')
                    ui.label(cliente.get('email', 'N/A')).classes('text-body1')

                with ui.column():
                    ui.label('Telefono:').classes('text-weight-bold')
                    ui.label(cliente.get('numeroTelefonico', 'N/A')).classes('text-body1')

                    ui.label('ID Cliente:').classes('text-weight-bold q-mt-md')
                    ui.label(str(cliente.get('id', 'N/A'))).classes('text-body1')

        # --- DIPENDENTE RESPONSABILE + CREATORE ---
        with ui.card().classes('q-pa-md q-mb-md').style('background:#e3f2fd;'):
            ui.label('DIPENDENTE RESPONSABILE').classes('text-h6 text-weight-bold q-mb-md')

            creato_da = servizio_json.get('creato_da')
            op_nome = op_cognome = ''
            if isinstance(creato_da, dict):
                op_nome = (creato_da.get('nome') or '').strip()
                op_cognome = (creato_da.get('cognome') or '').strip()
            operatore_display = (op_nome + ' ' + op_cognome).strip()

            if operatore_display:
                with ui.row().classes('items-center q-pa-xs q-mb-sm'):
                    ui.icon('person', size='18px').classes('q-mr-sm')
                    ui.label('Creato da:').classes('text-caption text-grey-6 q-mr-xs')
                    ui.label(operatore_display).classes('text-body1')

        # --- AZIONI ---
        with ui.row().classes('q-mt-lg justify-center'):
            if servizio.statoServizio in ['CREATO', 'IN_LAVORAZIONE']:
                ui.button(
                    'Modifica Servizio',
                    icon='edit',
                    on_click=lambda: ui.navigate.to(f'/servizi/{servizio_id}/modifica')
                ).classes('q-pa-md')

            ui.button(
                'Visualizza Documentazione',
                icon='folder',
                on_click=lambda: ui.navigate.to(f'/documentaizone_servizio_cliente/{servizio_id}')
            ).classes('q-pa-md')
