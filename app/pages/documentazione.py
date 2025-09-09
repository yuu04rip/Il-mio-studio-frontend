from nicegui import ui
from app.api.api import api_session
from app.components.components import header

API_BASE_URL = "http://localhost:8000"  # Aggiorna se il backend è su un altro indirizzo

TIPI_DOCUMENTO = [
    {"label": "Carta d'identità", "value": "carta_identita", "icon": "badge"},
    {"label": "Passaporto", "value": "passaporto", "icon": "flight"},
    {"label": "Tessera sanitaria", "value": "tessera_sanitaria", "icon": "medical_information"},
    {"label": "Patente", "value": "patente", "icon": "directions_car"},
]

def documentazione_page():
    header("Documentazione personale")
    user = api_session.user
    cliente_id = user.get('id') if user else None
    if not cliente_id:
        ui.label('Utente non autenticato').classes('text-negative')
        return

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto shadow-5').style('max-width:640px;background:#fafdff;'):
        ui.label('Gestisci i tuoi documenti personali').classes('text-h5 q-mb-xl').style(
            'background:#1976d2;color:white;border-radius:2em;padding:.6em 2.5em;display:block;text-align:center;font-weight:600;letter-spacing:0.04em;'
        )

        with ui.row().classes('q-mb-lg').style('justify-content:center;'):
            selected_tipo = ui.select(
                options={d["value"]: d["label"] for d in TIPI_DOCUMENTO},
                label='Tipo documento'
            ).props('outlined dense').classes('q-mr-md').style('min-width:220px;max-width:240px;')
            ui.upload(
                label='Carica documento',
                auto_upload=True,
                on_upload=lambda e: upload_documento(e, cliente_id, selected_tipo.value, after_upload)
            ).props('accept=.pdf,.jpg,.jpeg,.png color=primary flat').classes('q-px-md')

        ui.separator().classes('q-my-lg')

        doc_list = ui.column().classes('full-width').style('gap:20px;')

        def after_upload(success=True):
            if success:
                ui.notify("Documento caricato!", color='positive')
            else:
                ui.notify("Errore nel caricamento.", color='negative')
            refresh_docs()

        def refresh_docs():
            doc_list.clear()
            res = api_session.get(f'/documentazione/visualizza/{cliente_id}')
            if res.status_code == 200:
                docs = res.json()
                # Filtra solo i documenti non eliminati se il backend usa soft delete
                docs = [doc for doc in docs if not doc.get("is_deleted", False)]
                if docs:
                    for doc in docs:
                        tipo_label = next((d["label"] for d in TIPI_DOCUMENTO if d["value"] == doc["tipo"]), doc["tipo"])
                        tipo_icon = next((d["icon"] for d in TIPI_DOCUMENTO if d["value"] == doc["tipo"]), "description")
                        with doc_list:
                            with ui.card().style(
                                    'background:#f4f7fb;border-radius:1.5em;min-height:108px;padding:1.5em 2em;box-shadow:0 2px 14px 0 #0001;display:flex;align-items:center;'
                            ):
                                with ui.row().classes('items-center').style('width:100%;'):
                                    ui.icon(tipo_icon).style('font-size:2.3em;color:#1976d2;margin-right:20px;')
                                    with ui.column().style('flex:1;text-align:left;gap:0;'):
                                        ui.label(tipo_label).classes('text-body1').style('font-weight:700;font-size:1.18em;margin-bottom:3px;')
                                        ui.label(doc["filename"]).classes('text-blue-grey-7').style('font-size:1em;max-width:340px;overflow-x:auto;')
                                    ext = str(doc["filename"]).split('.')[-1].lower()
                                    with ui.row().classes('items-center').style('gap:8px;'):
                                        if ext in ["pdf", "jpg", "jpeg", "png"]:
                                            ui.button(
                                                '', icon='visibility', color='info',
                                                on_click=lambda d=doc: visualizza_documento(d['id'])
                                            ).props('round flat size=lg').classes('action-btn')
                                        ui.button(
                                            '', icon='download', color='primary',
                                            on_click=lambda d=doc: download_documento(d['id'])
                                        ).props('round flat size=lg').classes('action-btn')
                                        ui.button(
                                            '', icon='upload', color='purple',
                                            on_click=lambda d=doc: sostituisci_documento(d['id'], refresh_docs)
                                        ).props('round flat size=lg').classes('action-btn')
                else:
                    with doc_list:
                        ui.label('Nessun documento caricato.').classes('text-grey-7 q-mt-md').style('text-align:center;font-size:1.12em;')
            else:
                with doc_list:
                    ui.label('Errore nel recupero documenti').classes('text-negative')

        refresh_docs()

    ui.add_head_html("""
    <style>
    .action-btn {
        transition: background .2s, box-shadow .2s;
        margin: 0 4px !important;
        box-shadow: none !important;
    }
    .action-btn:hover {
        background: #e3e7fb !important;
        box-shadow: 0 1px 8px 0 #1976d241 !important;
        transform: scale(1.08);
    }
    .q-card {
        border: none !important;
    }
    </style>
    """)

def upload_documento(event, cliente_id, tipo, callback):
    if not tipo:
        ui.notify("Seleziona il tipo di documento!", color='negative')
        callback(False)
        return
    import requests
    url = API_BASE_URL + '/documentazione/carica'
    headers = api_session.get_headers() if hasattr(api_session, 'get_headers') else {}
    files = {'file': (event.name, event.content, event.type)}
    data = {'cliente_id': str(cliente_id), 'tipo': tipo}
    try:
        resp = requests.post(url, data=data, files=files, headers=headers)
        callback(resp.status_code == 200)
    except Exception:
        callback(False)

def download_documento(doc_id):
    url = f"{API_BASE_URL}/documentazione/download/{doc_id}"
    ui.run_javascript(f"window.open('{url}', '_blank')")

def visualizza_documento(doc_id):
    url = f"{API_BASE_URL}/documentazione/download/{doc_id}"
    ui.run_javascript(f"window.open('{url}', '_blank')")

def sostituisci_documento(doc_id, refresh_callback):
    def on_upload(event):
        import requests
        url = API_BASE_URL + f'/documentazione/sostituisci/{doc_id}'
        headers = api_session.get_headers() if hasattr(api_session, 'get_headers') else {}
        files = {'file': (event.name, event.content, event.type)}
        try:
            resp = requests.put(url, files=files, headers=headers)
            if resp.status_code == 200:
                ui.notify("Documento sostituito!", color='positive')
            else:
                ui.notify("Errore nella sostituzione.", color='negative')
        except Exception:
            ui.notify("Errore nella sostituzione.", color='negative')
        refresh_callback()
    ui.upload(label='Sostituisci documento', auto_upload=True, on_upload=on_upload).props(
        'accept=.pdf,.jpg,.jpeg,.png color=accent flat'
    )