from nicegui import ui, app
from app.api.api import api_session
from app.components.components import header
import tempfile
import os
from threading import Timer
from mimetypes import guess_type
import uuid
from typing import Dict, Optional
from starlette.responses import FileResponse, Response

API_BASE = "http://localhost:8000"

# mappa preview_id -> (path, mime, filename) per questo modulo
_PREVIEW_FILES_DOC: Dict[str, dict] = {}

TIPI_DOCUMENTO = [
    {"label": "Carta d'identità", "value": "carta_identita", "icon": "badge"},
    {"label": "Passaporto", "value": "passaporto", "icon": "flight"},
    {"label": "Tessera sanitaria", "value": "tessera_sanitaria", "icon": "medical_information"},
    {"label": "Patente", "value": "patente", "icon": "directions_car"},
]

TIPI_DOCUMENTO_SERVIZIO = [
    {"label": "Visure catastali", "value": "visure_catastali", "icon": "assignment"},
    {"label": "Planimetria", "value": "planimetria", "icon": "map"},
    {"label": "Atto", "value": "atto", "icon": "gavel"},
    {"label": "Compromesso", "value": "compromesso", "icon": "description"},
    {"label": "Preventivo", "value": "preventivo", "icon": "attach_money"},
]


# --- Routes per preview (raw + wrapper) ---
@app.get('/__preview_doc_raw/{preview_id}')
def _serve_preview_doc_raw(preview_id: str):
    info = _PREVIEW_FILES_DOC.get(preview_id)
    if not info:
        return Response('Not found', status_code=404)
    path = info.get('path')
    mime = info.get('mime') or 'application/octet-stream'
    if not path or not os.path.exists(path):
        return Response('Not found', status_code=404)
    return FileResponse(path, media_type=mime)


@app.get('/__preview_doc/{preview_id}')
def _serve_preview_doc_wrapper(preview_id: str):
    info = _PREVIEW_FILES_DOC.get(preview_id)
    if not info:
        return Response('Not found', status_code=404)
    mime = info.get('mime') or 'application/octet-stream'
    filename = info.get('filename') or 'Anteprima'
    if mime.startswith('image/'):
        html = f'''
        <!doctype html>
        <html>
          <head><meta charset="utf-8"><title>{filename}</title><meta name="viewport" content="width=device-width, initial-scale=1">
          <style>html,body{{height:100%;margin:0;background:#111;display:flex;align-items:center;justify-content:center}}img{{max-width:100%;max-height:100vh;object-fit:contain}}.controls{{position:fixed;top:10px;right:10px;z-index:999}}.btn{{background:#1976d2;color:white;padding:8px 12px;border-radius:6px;text-decoration:none;font-family:Arial}}</style>
          </head>
          <body>
            <div class="controls"><a class="btn" href="/__preview_doc_raw/{preview_id}" target="_blank" rel="noopener">Apri originale</a></div>
            <img src="/__preview_doc_raw/{preview_id}" alt="preview">
          </body>
        </html>
        '''
    else:
        html = f'''
        <!doctype html>
        <html>
          <head><meta charset="utf-8"><title>{filename}</title><meta name="viewport" content="width=device-width, initial-scale=1">
          <style>html,body{{height:100%;margin:0}} iframe{{border:none;width:100%;height:100vh}} .topbar{{position:fixed;top:8px;left:8px;right:8px;z-index:999;display:flex;justify-content:flex-end;gap:8px}} .btn{{background:#1976d2;color:white;padding:6px 10px;border-radius:6px;text-decoration:none;font-family:Arial}}</style>
          </head>
          <body>
            <div class="topbar">
              <a class="btn" href="/__preview_doc_raw/{preview_id}" target="_blank" rel="noopener">Apri originale</a>
              <a class="btn" href="javascript:location.reload()">Ricarica</a>
            </div>
            <iframe src="/__preview_doc_raw/{preview_id}"></iframe>
          </body>
        </html>
        '''
    return Response(html, media_type='text/html')


# helper: preview, download
def _preview_documento(doc: dict):
    try:
        content = api_session.download_documentazione(doc['id'])
    except Exception as e:
        ui.notify(f"Errore preview: {e}", color='negative')
        return

    if not content:
        ui.notify("Errore: contenuto vuoto", color='negative')
        return

    max_preview_size = 50 * 1024 * 1024
    if len(content) > max_preview_size:
        ui.notify("File troppo grande per la preview: scaricalo.", color='warning')
        return

    mime, _ = guess_type(doc.get('filename') or '')
    mime = mime or 'application/octet-stream'
    suffix = os.path.splitext(doc.get('filename') or '')[1] or ''
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp.write(content)
        tmp.flush()
        tmp.close()
    except Exception as e:
        try:
            tmp.close()
        except Exception:
            pass
        if os.path.exists(tmp.name):
            try:
                os.unlink(tmp.name)
            except Exception:
                pass
        ui.notify(f"Errore salvataggio temporaneo: {e}", color='negative')
        return

    preview_id = uuid.uuid4().hex
    _PREVIEW_FILES_DOC[preview_id] = {'path': tmp.name, 'mime': mime, 'filename': doc.get('filename') or f'doc_{doc["id"]}{suffix}'}

    def _cleanup(pid):
        info = _PREVIEW_FILES_DOC.pop(pid, None)
        if info:
            try:
                if os.path.exists(info['path']):
                    os.remove(info['path'])
            except Exception:
                pass

    Timer(120.0, _cleanup, args=(preview_id,)).start()
    try:
        ui.run_javascript(f"window.open('/__preview_doc/{preview_id}', '_blank');")
    except Exception as e:
        ui.notify(f"Errore apertura nuova scheda: {e}", color='negative')


def _proxy_download_doc(doc: dict):
    try:
        content = api_session.download_documentazione(doc['id'])
    except Exception as e:
        ui.notify(f"Errore download: {e}", color='negative')
        return
    if not content:
        ui.notify("Errore: contenuto vuoto", color='negative')
        return

    filename = doc.get('filename') or f'documento_{doc["id"]}'
    suffix = os.path.splitext(filename)[1] if '.' in filename else ''
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp_file.write(content)
        tmp_file.flush()
        tmp_file.close()
    except Exception as e:
        try:
            tmp_file.close()
        except Exception:
            pass
        if os.path.exists(tmp_file.name):
            try:
                os.unlink(tmp_file.name)
            except Exception:
                pass
        ui.notify(f"Errore salvataggio temporaneo: {e}", color='negative')
        return

    try:
        ui.download(tmp_file.name, filename)
    except Exception as e:
        ui.notify(f"Errore download client: {e}", color='negative')
        if os.path.exists(tmp_file.name):
            try:
                os.unlink(tmp_file.name)
            except Exception:
                pass
    def _cleanup(path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    Timer(60.0, _cleanup, args=(tmp_file.name,)).start()


async def upload_documento(event, target_id, tipo, callback):
    """
    target_id: servizio_id or cliente_id depending on context
    tipo: tipo documento (string)
    callback: function(success: bool)
    """
    if not tipo:
        ui.notify("Seleziona il tipo di documento!", color='negative')
        try:
            callback(False)
        except Exception:
            pass
        return
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file_bytes = await event.file.read()
        tmp.write(file_bytes)
        tmp.flush()
        tmp_path = tmp.name
    try:
        # decide quale API chiamare in base al contesto: se target_id rappresenta servizio (int) e endpoint supporta servizio -> usa carica_documentazione_servizio
        # here we call carica_documentazione_servizio for consistency (frontend previously used it).
        api_session.carica_documentazione_servizio(target_id, tipo, tmp_path, filename=event.file.name)
        try:
            callback(True)
        except Exception:
            pass
    except Exception as ex:
        ui.notify(f"Errore upload: {ex}", color='negative')
        try:
            callback(False)
        except Exception:
            pass
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def elimina_documento(servizio_id, doc_id, refresh_callback):
    def conferma_eliminazione():
        try:
            api_session.elimina_documentazione_servizio(servizio_id, doc_id)
            ui.notify("Documento eliminato!", color='positive')
        except Exception:
            ui.notify("Errore nell'eliminazione.", color='negative')
        try:
            dialog.close()
        except Exception:
            pass
        if callable(refresh_callback):
            try:
                refresh_callback()
            except Exception:
                pass

    dialog = ui.dialog().props('persistent')
    with dialog, ui.card().classes('q-pa-md').style('max-width:340px;'):
        ui.label('Confermi di voler eliminare questo documento?')
        with ui.row():
            ui.button('Elimina', color='negative', on_click=conferma_eliminazione)
            ui.button('Annulla', on_click=dialog.close)
    dialog.open()


# -------- _render_doc_row definita prima dell'uso --------
def _render_doc_row(doc: dict, container, is_service: bool = False, servizio_id: Optional[int] = None, refresh_callback=None):
    filename = doc.get("filename") or f"documento_{doc.get('id')}"
    tipo_label = doc.get("tipo") or doc.get("label") or "Documento"
    ext = str(filename).split('.')[-1].lower() if filename and '.' in filename else ''
    tipo_icon = "description"
    with container:
        with ui.card().style('background:#f4f7fb;border-radius:1.5em;min-height:72px;padding:1em 1.4em;margin-bottom:8px;'):
            with ui.row().classes('items-center').style('width:100%;gap:12px;'):
                ui.icon(tipo_icon).style('font-size:1.8em;color:#1976d2;margin-right:12px;')
                with ui.column().style('flex:1;text-align:left;'):
                    ui.label(tipo_label).classes('text-body1').style('font-weight:700')
                    ui.label(filename).classes('text-grey-7').style('font-size:0.95em;max-width:420px;overflow-x:auto;word-break:break-all;')
                with ui.row().classes('items-center').style('gap:8px;'):
                    if ext in ["pdf", "jpg", "jpeg", "png"]:
                        btn_preview = ui.button('', icon='visibility', color='info').props('round flat size=lg type=button').classes('action-btn')
                        btn_preview.on('click', lambda e, d=doc: _preview_documento(d))
                    btn_dl = ui.button('', icon='download', color='primary').props('round flat size=lg type=button').classes('action-btn')
                    btn_dl.on('click', lambda e, d=doc: _proxy_download_doc(d))
                    if is_service:
                        # attach confirmation dialog and delete action
                        def _attach_confirm(_doc=doc):
                            dlg = ui.dialog().props('persistent')
                            with dlg, ui.card().classes('q-pa-md').style('max-width:360px;'):
                                ui.label('Confermi di voler eliminare questo documento?').classes('q-mb-md')
                                with ui.row().style('justify-content:flex-end;gap:8px;'):
                                    ui.button('Elimina', color='negative', on_click=lambda: (dlg.close(), api_session.elimina_documentazione_servizio(servizio_id, _doc['id']), ui.notify("Documento eliminato!", color='positive'), refresh_callback() if callable(refresh_callback) else None))
                                    ui.button('Annulla', on_click=dlg.close)
                            dlg.open()
                        btn_del = ui.button('', icon='delete', color='negative').props('round flat size=lg type=button').classes('action-btn')
                        btn_del.on('click', lambda e, _f=_attach_confirm: _f())


# -------- Pagina documentazione (unica funzione, servizio_id opzionale) --------
def documentazione_servizio_page(servizio_id: Optional[int] = None):
    ui.add_head_html("""
<style>
.q-uploader {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}
.q-uploader__list {
    display: none !important; /* nasconde il riquadro bianco */
}
.custom-uploader .q-uploader__header {
    border: none !important;
    box-shadow: none !important;
}
.custom-uploader {
    background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;
    font-weight: 600 !important;
    border-radius: 2.5em !important;
    box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important;
}
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
</style>
""")
    header('Documentazione' + (f' servizio #{servizio_id}' if servizio_id else ''))
    user = api_session.user
    cliente_id = user.get('id') if user else None
    if not cliente_id and servizio_id is None:
        ui.label('Utente non autenticato').classes('text-negative')
        return

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto shadow-5').style(
            'max-width:880px;background: rgba(240,240,240) !important; '
            'box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important; '
            'border-radius: 2.5em !important; align-items:center;'
    ):
        ui.label('Documentazione').classes('text-h5 q-mb-xl').style(
            'background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;'
            'color:white;border-radius:2em;padding:.6em 2.5em;display:block;text-align:center;'
            'font-weight:600;letter-spacing:0.04em;'
        )

        # upload area
        with ui.row().classes('q-mb-lg').style('justify-content:center;'):
            # choose correct tipi list depending on whether we're in servizio context
            tipi_opts = TIPI_DOCUMENTO_SERVIZIO if servizio_id else TIPI_DOCUMENTO
            selected_tipo = ui.select(options={d["value"]: d["label"] for d in tipi_opts}, label='Tipo documento').props('outlined dense').classes('q-mr-md').style('min-width:220px;max-width:240px;')
            # choose target id (if servizio_id provided we upload to servizio, else to personal cliente_id)
            target_id = servizio_id if servizio_id is not None else cliente_id

            async def _on_upload(e):
                await upload_documento(e, target_id, selected_tipo.value, lambda ok: (ui.notify("Documento caricato!", color='positive') if ok else ui.notify("Errore caricamento", color='negative')))

            ui.upload(label='Carica documento', auto_upload=True, on_upload=_on_upload).props('accept=.pdf,.jpg,.jpeg,.png flat').classes('custom-uploader')

        ui.separator().classes('q-my-lg')

        container = ui.column().classes('full-width').style('gap:20px;')

        def refresh_docs():
            container.clear()
            # documenti del servizio (se applicabile)
            if servizio_id is not None:
                try:
                    resp_srv = api_session.get(f'/documentazione/servizi/{servizio_id}/documenti')
                    srv_docs = resp_srv.json() if resp_srv.status_code == 200 else []
                except Exception:
                    srv_docs = []
                srv_docs = [d for d in srv_docs if not d.get('is_deleted', False)]
                with container:
                    ui.label('Documenti del servizio').classes('text-h6 q-mb-sm')
                    if srv_docs:
                        for doc in srv_docs:
                            _render_doc_row(doc, container, is_service=True, servizio_id=servizio_id, refresh_callback=refresh_docs)
                    else:
                        ui.label('Nessun documento associato al servizio.').classes('text-grey-7')

            # documenti personali del cliente
            cliente_id_local = cliente_id
            if not cliente_id_local and servizio_id is not None:
                try:
                    srv_resp = api_session.get(f'/studio/servizi/{servizio_id}')
                    if srv_resp.status_code == 200:
                        srv = srv_resp.json()
                        cliente_id_local = srv.get('cliente_id')
                except Exception:
                    cliente_id_local = None

            with container:
                ui.label('Documenti personali del cliente').classes('text-h6 q-mt-md q-mb-sm')
                if cliente_id_local:
                    try:
                        resp = api_session.get(f'/documentazione/documenti/visualizza/{cliente_id_local}')
                        client_docs = resp.json() if resp.status_code == 200 else []
                    except Exception:
                        client_docs = []
                    client_docs = [d for d in client_docs if not d.get('is_deleted', False)]
                    if client_docs:
                        for doc in client_docs:
                            _render_doc_row(doc, container, is_service=False)
                    else:
                        ui.label('Nessun documento personale caricato.').classes('text-grey-7')
                else:
                    ui.label('Cliente non identificato: impossibile recuperare documenti personali.').classes('text-negative')

        refresh_docs()