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


def servizio_cliente_dettagli_page(cliente_id: int, servizio_id: int):
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
    width: 100% !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    letter-spacing: 0.5px !important;
    heigth:100 px;
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
    """Pagina dettagli servizio per il cliente"""

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto').style(
            'width: 550px;background: rgba(240,240,240) !important;box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important;border-radius: 2.5em !important;border: 1.7px solid #e3eaf1 !important;backdrop-filter: blur(6px);align-items:center;'
    ):
        with ui.row().classes('items-center q-mb-lg').style('width:100%;gap:12px;justify-content: center;'):
            ui.label('DETTAGLI SERVIZIO').classes('text-h4 text-weight-bold').style('color: #1976d2;align-items:center')

        try:
            servizio_data = api_session.get(f'/studio/servizi/{servizio_id}')
            servizio_data.raise_for_status()
            servizio_json = servizio_data.json()
            servizio = Servizio.from_dict(servizio_json)

            cliente_data = api_session.get(f'/studio/clienti/{servizio.cliente_id}/dettagli')
            cliente_data.raise_for_status()
            cliente = cliente_data.json()
        except Exception as e:
            ui.notify(f"Errore nel caricamento dei dettagli: {e}", color="negative")
            ui.label("Impossibile caricare i dettagli del servizio").classes('text-negative q-mt-md')
            return

        # --- INFORMAZIONI PRINCIPALI + CREATORE ---
        with ui.card().classes('q-pa-md q-mb-md').style('background:#f5f5f5;width:400px;'):
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
                        ui.label(servizio.statoServizio).classes('text-body1')

                    # Creatore del servizio
                    creato_da = servizio_json.get('creato_da')
                    op_nome = op_cognome = ''
                    if isinstance(creato_da, dict):
                        op_nome = (creato_da.get('nome') or '').strip()
                        op_cognome = (creato_da.get('cognome') or '').strip()
                    operatore_display = (op_nome + ' ' + op_cognome).strip()

                    if operatore_display:
                        ui.label('Creato da:').classes('text-weight-bold q-mt-md')
                        with ui.row().classes('items-center'):
                            ui.icon('person', size='18px').classes('q-mr-xs')
                            ui.label(operatore_display).classes('text-body1')

                with ui.column():
                    ui.label('Codice Corrente:').classes('text-weight-bold')
                    ui.label(str(servizio.codiceCorrente)).classes('text-body1')

                    # Data Richiesta
                    ui.label('Data Richiesta:').classes('text-weight-bold q-mt-md')
                    try:
                        data_richiesta_dt = datetime.fromisoformat(servizio.dataRichiesta) \
                            if isinstance(servizio.dataRichiesta, str) else servizio.dataRichiesta
                        data_richiesta_str = data_richiesta_dt.strftime('%d/%m/%Y %H:%M')
                    except Exception:
                        data_richiesta_str = servizio.dataRichiesta
                    ui.label(data_richiesta_str).classes('text-body1')

                    # Data Consegna +3 mesi
                    ui.label('Data Consegna:').classes('text-weight-bold q-mt-md')
                    try:
                        data_consegna_dt = datetime.fromisoformat(servizio.dataConsegna) \
                            if isinstance(servizio.dataConsegna, str) else servizio.dataConsegna
                        data_consegna_plus3 = data_consegna_dt + relativedelta(months=+3)
                        data_consegna_str = data_consegna_plus3.strftime('%d/%m/%Y %H:%M')
                    except Exception:
                        data_consegna_str = servizio.dataConsegna
                    ui.label(data_consegna_str).classes('text-body1')

        # --- DATI CLIENTE ---
        with ui.card().classes('q-pa-md q-mb-md').style('background:#e8f5e8;width:400px;'):
            ui.label('I TUOI DATI').classes('text-h6 text-weight-bold q-mb-md')
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

        # --- AZIONI ---
        with ui.row().classes('q-mt-lg justify-center'):
            ui.button(
                'Visualizza Documentazione',
                icon='folder',
                on_click=lambda: ui.navigate.to(f'/documentaizone_servizio_cliente/{servizio_id}')
            ).classes('custom-button-blue-light')

