from nicegui import ui
from app.api.api import api_session
from app.components.components import header
import tempfile
import os

TIPI_DOCUMENTO_SERVIZIO = [
    {"label": "Visure catastali", "value": "visure_catastali", "icon": "assignment"},
    {"label": "Planimetria", "value": "planimetria", "icon": "map"},
    {"label": "Atto", "value": "atto", "icon": "gavel"},
    {"label": "Compromesso", "value": "compromesso", "icon": "description"},
    {"label": "Preventivo", "value": "preventivo", "icon": "attach_money"},
]

def documentazione_servizio_page(servizio_id: int):
    header(f"Documentazione servizio #{servizio_id}")
    user = api_session.user
    dipendente_id = api_session.get_dipendente_id_by_user(user['id']) if user else None
    if not dipendente_id:
        ui.label('Utente non autenticato o non dipendente tecnico').classes('text-negative')
        return

    try:
        servizio_data = api_session.get(f'/studio/servizi/{servizio_id}')
        servizio_data.raise_for_status()
        servizio = servizio_data.json()
        cliente_id = servizio.get('cliente_id')
    except Exception as e:
        ui.notify(f"Errore nel recupero del servizio: {e}", color="negative")
        cliente_id = None

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto shadow-5').style('max-width:760px;background:#fafdff;'):
        ui.label('Documenti del servizio').classes('text-h5 q-mb-xl').style(
            'background:#1976d2;color:white;border-radius:2em;padding:.6em 2.5em;display:block;text-align:center;font-weight:600;letter-spacing:0.04em;'
        )

        with ui.row().classes('q-mb-lg').style('justify-content:center;'):
            selected_tipo = ui.select(
                options={d["value"]: d["label"] for d in TIPI_DOCUMENTO_SERVIZIO},
                label='Tipo documento'
            ).props('outlined dense').classes('q-mr-md').style('min-width:220px;max-width:240px;')

            async def handle_upload(e):
                await upload_documento(e, servizio_id, selected_tipo.value, after_upload)

            ui.upload(
                label='Carica documento',
                auto_upload=True,
                on_upload=handle_upload
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
            try:
                docs = api_session.visualizza_documentazione_servizio(servizio_id)
            except Exception:
                docs = []
            docs = [doc for doc in docs if not doc.get("is_deleted", False)]
            if docs:
                for doc in docs:
                    tipo_label = next((d["label"] for d in TIPI_DOCUMENTO_SERVIZIO if d["value"] == doc.get("tipo")), doc.get("tipo"))
                    tipo_icon = next((d["icon"] for d in TIPI_DOCUMENTO_SERVIZIO if d["value"] == doc.get("tipo")), "description")
                    with doc_list:
                        with ui.card().style(
                                'background:#f4f7fb;border-radius:1.5em;min-height:108px;padding:1.5em 2em;box-shadow:0 2px 14px 0 #0001;display:flex;align-items:center;'
                        ):
                            with ui.row().classes('items-center').style('width:100%;'):
                                ui.icon(tipo_icon).style('font-size:2.3em;color:#1976d2;margin-right:20px;')
                                with ui.column().style('flex:1;text-align:left;gap:0;'):
                                    ui.label(tipo_label).classes('text-body1').style('font-weight:700;font-size:1.18em;margin-bottom:3px;')
                                    ui.label(doc.get("filename", "Documento")).classes('text-blue-grey-7').style('font-size:1em;max-width:340px;overflow-x:auto;')
                                ext = str(doc.get("filename", "")).split('.')[-1].lower()
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
                                        '', icon='delete', color='negative',
                                        on_click=lambda d=doc: elimina_documento(servizio_id, d['id'], refresh_docs)
                                    ).props('round flat size=lg').classes('action-btn')
            else:
                with doc_list:
                    ui.label('Nessun documento caricato.').classes('text-grey-7 q-mt-md').style('text-align:center;font-size:1.12em;')

        refresh_docs()

        if cliente_id:
            ui.separator().classes('q-my-xl')
            ui.label('Documenti personali del cliente').classes('text-h6 q-mb-md').style(
                'background:#7cb342;color:white;border-radius:2em;padding:.4em 1.6em;display:inline-block;text-align:center;font-weight:600;letter-spacing:0.04em;'
            )
            doc_cliente_list = ui.column().classes('full-width').style('gap:20px;')

            try:
                doc_cliente = api_session.visualizza_documentazione_cliente(cliente_id)
            except Exception:
                doc_cliente = []
            doc_cliente = [doc for doc in doc_cliente if not doc.get("is_deleted", False)]
            if doc_cliente:
                for doc in doc_cliente:
                    with doc_cliente_list:
                        with ui.card().style('background:#e8f5e9;border-radius:1.5em;min-height:72px;padding:1em 2em;margin-bottom:8px;'):
                            ui.label(doc.get("filename", "Documento")).classes('text-body1 text-blue-grey-8')
                            ext = str(doc.get("filename", "")).split('.')[-1].lower()
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
            else:
                with doc_cliente_list:
                    ui.label('Nessun documento personale caricato dal cliente.').classes('text-grey-7 q-mt-md')

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

async def upload_documento(event, servizio_id, tipo, callback):
    if not tipo:
        ui.notify("Seleziona il tipo di documento!", color='negative')
        callback(False)
        return
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file_bytes = await event.file.read()
        tmp.write(file_bytes)
        tmp.flush()
        tmp_path = tmp.name
    try:
        tipo_backend = tipo
        api_session.carica_documentazione_servizio(
            servizio_id, tipo_backend, tmp_path, filename=event.file.name
        )
        callback(True)
    except Exception as ex:
        ui.notify(f"Errore upload: {ex}", color='negative')
        callback(False)
    finally:
        os.remove(tmp_path)

def download_documento(doc_id):
    url = f"http://localhost:8000/documentazione/download/{doc_id}"
    ui.run_javascript(f"window.open('{url}', '_blank')")

def visualizza_documento(doc_id):
    url = f"http://localhost:8000/documentazione/download/{doc_id}"
    ui.run_javascript(f"window.open('{url}', '_blank')")

def elimina_documento(servizio_id, doc_id, refresh_callback):
    def conferma_eliminazione():
        try:
            api_session.elimina_documentazione_servizio(servizio_id, doc_id)
            ui.notify("Documento eliminato!", color='positive')
        except Exception:
            ui.notify("Errore nell'eliminazione.", color='negative')
        refresh_callback()
        dialog.close()

    dialog = ui.dialog().props('persistent')
    with dialog, ui.card().classes('q-pa-md').style('max-width:340px;'):
        ui.label('Confermi di voler eliminare questo documento?')
        with ui.row():
            ui.button('Elimina', color='negative', on_click=conferma_eliminazione)
            ui.button('Annulla', on_click=dialog.close)
    dialog.open()