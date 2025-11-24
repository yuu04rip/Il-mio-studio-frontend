from nicegui import ui, app
from app.api.api import api_session
from app.components.components import header
import requests
import tempfile
import os
from threading import Timer
import base64
from mimetypes import guess_type
import json
import uuid
from typing import Dict
from starlette.responses import FileResponse, Response

API_BASE_URL = "http://localhost:8000"

# mappa id -> (path, mime, filename)
_PREVIEW_FILES: Dict[str, dict] = {}

TIPI_DOCUMENTO = [
    {"label": "Carta d'identità", "value": "carta_identita", "icon": "badge"},
    {"label": "Passaporto", "value": "passaporto", "icon": "flight"},
    {"label": "Tessera sanitaria", "value": "tessera_sanitaria", "icon": "medical_information"},
    {"label": "Patente", "value": "patente", "icon": "directions_car"},
]


def documentazione_page():
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

</style>
""")
    user = api_session.user
    cliente_id = user.get('id') if user else None
    if not cliente_id:
        ui.label('Utente non autenticato').classes('text-negative')
        return

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto shadow-5').style(
            'max-width:640px;background: rgba(240,240,240) !important; '
            'box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important; '
            'border-radius: 2.5em !important; align-items:center;'
    ):
        ui.label('Documenti personali').classes('text-h5 q-mb-xl').style(
            'background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;'
            'color:white;border-radius:2em;padding:.6em 2.5em;display:block;text-align:center;'
            'font-weight:600;letter-spacing:0.04em;'
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
            ).props('accept=.pdf,.jpg,.jpeg,.png flat').classes('custom-uploader')

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
            res = api_session.get(f'/documentazione/documenti/visualizza/{cliente_id}')
            if res.status_code == 200:
                docs = res.json()
                docs = [doc for doc in docs if not doc.get("is_deleted", False)]
                docs = [doc for doc in docs if doc.get("tipo") in [d["value"] for d in TIPI_DOCUMENTO]]
                if docs:
                    for doc in docs:
                        tipo_label = next((d["label"] for d in TIPI_DOCUMENTO if d["value"] == doc["tipo"]), doc["tipo"])
                        tipo_icon = next((d["icon"] for d in TIPI_DOCUMENTO if d["value"] == doc["tipo"]), "description")
                        with doc_list:
                            with ui.card().style(
                                    'background:#f4f7fb;border-radius:1.5em;min-height:108px;padding:1.5em 2em;'
                                    'box-shadow:0 2px 14px 0 #0001;display:flex;align-items:center;'
                            ):
                                with ui.row().classes('items-center').style('width:100%;'):
                                    ui.icon(tipo_icon).style('font-size:2.3em;color:#1976d2;margin-right:20px;')
                                    with ui.column().style('flex:1;text-align:left;gap:0;'):
                                        ui.label(tipo_label).classes('text-body1').style(
                                            'font-weight:700;font-size:1.18em;margin-bottom:3px;'
                                        )
                                        ui.label(doc["filename"]).classes('text-blue-grey-7').style(
                                            'font-size:1em;max-width:340px;overflow-x:auto;'
                                        )
                                    ext = str(doc["filename"]).split('.')[-1].lower()
                                    with ui.row().classes('items-center').style('gap:8px;'):
                                        # Visualizza (preview) solo per tipi visualizzabili
                                        if ext in ["pdf", "jpg", "jpeg", "png"]:
                                            ui.button(
                                                '', icon='visibility', color='info',
                                                on_click=lambda d=doc: _preview_documento(d)
                                            ).props('round flat size=lg').classes('action-btn')
                                        ui.button(
                                            '', icon='download', color='primary',
                                            on_click=lambda d=doc: _proxy_download_doc(d)
                                        ).props('round flat size=lg').classes('action-btn')
                                        ui.button(
                                            '', icon='upload', color='purple',
                                            on_click=lambda d=doc: sostituisci_documento(d['id'], refresh_docs)
                                        ).props('round flat size=lg').classes('q-ml-sm action-btn')
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


async def upload_documento(event, cliente_id, tipo, callback):
    if not tipo:
        ui.notify("Seleziona il tipo di documento!", color='negative')
        if callback:
            callback(False)
        return
    filename = getattr(event.file, 'name', 'documento')
    mimetype = getattr(event, 'type', 'application/octet-stream')
    content = await event.file.read()
    files = {'file': (filename, content, mimetype)}
    data = {'cliente_id': str(cliente_id), 'tipo': tipo}
    headers = api_session.get_headers() if hasattr(api_session, 'get_headers') else {}
    try:
        resp = requests.post(f"{API_BASE_URL}/documentazione/documenti/carica", data=data, files=files, headers=headers)
        if callback:
            callback(resp.status_code == 200)
    except Exception:
        if callback:
            callback(False)


def sostituisci_documento(doc_id, refresh_callback):
    async def on_upload(event):
        filename = getattr(event.file, 'name', 'documento')
        mimetype = getattr(event, 'type', 'application/octet-stream')
        content = await event.file.read()
        files = {'file': (filename, content, mimetype)}
        headers = api_session.get_headers() if hasattr(api_session, 'get_headers') else {}
        try:
            resp = requests.put(f"{API_BASE_URL}/documentazione/documenti/sostituisci/{doc_id}", files=files, headers=headers)
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


def _proxy_download_doc(doc: dict):
    """
    Proxy server-side download:
    - scarica i bytes dal backend usando api_session (server->backend)
    - salva in file temporaneo e chiama ui.download(path, filename)
    - programma la cancellazione del file temporaneo
    """
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
        return

    def _cleanup(path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    Timer(60.0, _cleanup, args=(tmp_file.name,)).start()


@app.get('/__preview_raw/{preview_id}')
def _serve_preview_raw(preview_id: str):
    """Serve il file grezzo senza forzare Content-Disposition."""
    info = _PREVIEW_FILES.get(preview_id)
    if not info:
        return Response('Not found', status_code=404)
    path = info.get('path')
    mime = info.get('mime') or 'application/octet-stream'
    if not path or not os.path.exists(path):
        return Response('Not found', status_code=404)
    return FileResponse(path, media_type=mime)


@app.get('/__preview/{preview_id}')
def _serve_preview_wrapper(preview_id: str):
    """
    Pagina wrapper che mostra il file (iframe per PDF/altro, img per immagini).
    Questo evita che il browser scarichi direttamente il file e ti dà controllo
    sul layout/resolution.
    """
    info = _PREVIEW_FILES.get(preview_id)
    if not info:
        return Response('Not found', status_code=404)
    mime = info.get('mime') or 'application/octet-stream'
    filename = info.get('filename') or 'Anteprima'
    # HTML wrapper
    if mime.startswith('image/'):
        html = f'''
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8">
            <title>{filename}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
              html,body{{height:100%;margin:0;background:#111;display:flex;align-items:center;justify-content:center}}
              img{{max-width:100%;max-height:100vh;object-fit:contain}}
              .controls{{position:fixed;top:10px;right:10px;z-index:999}}
              .btn{{background:#1976d2;color:white;padding:8px 12px;border-radius:6px;text-decoration:none;font-family:Arial}}
            </style>
          </head>
          <body>
            <div class="controls"><a class="btn" href="/__preview_raw/{preview_id}" target="_blank" rel="noopener">Apri originale</a></div>
            <img src="/__preview_raw/{preview_id}" alt="preview">
          </body>
        </html>
        '''
    else:
        # PDF o altri documenti visualizzabili
        html = f'''
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8">
            <title>{filename}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
              html,body{{height:100%;margin:0}}
              iframe{{border:none;width:100%;height:100vh}}
              .topbar{{position:fixed;top:8px;left:8px;right:8px;z-index:999;display:flex;justify-content:flex-end;gap:8px}}
              .btn{{background:#1976d2;color:white;padding:6px 10px;border-radius:6px;text-decoration:none;font-family:Arial}}
            </style>
          </head>
          <body>
            <div class="topbar">
              <a class="btn" href="/__preview_raw/{preview_id}" target="_blank" rel="noopener">Apri originale</a>
              <a class="btn" href="javascript:location.reload()">Ricarica</a>
            </div>
            <iframe src="/__preview_raw/{preview_id}"></iframe>
          </body>
        </html>
        '''
    return Response(html, media_type='text/html')


def _preview_documento(doc: dict):
    """
    Scarica i bytes dal backend, salva in file temporaneo e apre una nuova scheda
    che punta a /__preview/{preview_id} (wrapper HTML).
    """
    try:
        content = api_session.download_documentazione(doc['id'])
    except Exception as e:
        ui.notify(f"Errore preview: {e}", color='negative')
        return

    if not content:
        ui.notify("Errore: contenuto vuoto", color='negative')
        return

    # Limite opzionale per evitare di creare troppi file giganti in memoria
    max_preview_size = 50 * 1024 * 1024  # 50 MB
    if len(content) > max_preview_size:
        ui.notify("File troppo grande per la preview: scaricalo.", color='warning')
        return

    mime, _ = guess_type(doc.get('filename') or '')
    mime = mime or 'application/octet-stream'

    # crea file temporaneo
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

    # registra nella mappa con id univoco
    preview_id = uuid.uuid4().hex
    _PREVIEW_FILES[preview_id] = {
        'path': tmp.name,
        'mime': mime,
        'filename': doc.get('filename') or f'doc_{doc["id"]}{suffix}'
    }

    # programma la cancellazione dopo 120 secondi (rimuove file e entry dalla mappa)
    def _cleanup(pid):
        info = _PREVIEW_FILES.pop(pid, None)
        if info:
            try:
                if os.path.exists(info['path']):
                    os.remove(info['path'])
            except Exception:
                pass

    Timer(120.0, _cleanup, args=(preview_id,)).start()

    # Apri nuova scheda verso il wrapper HTML che mostra il file dentro iframe/img
    try:
        ui.run_javascript(f"window.open('/__preview/{preview_id}', '_blank');")
    except Exception as e:
        ui.notify(f"Errore apertura nuova scheda: {e}", color='negative')
