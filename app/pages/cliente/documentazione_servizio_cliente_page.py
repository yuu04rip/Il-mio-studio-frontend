from nicegui import ui, app
from app.api.api import api_session
import tempfile
import os
from threading import Timer
import base64
from mimetypes import guess_type
import json
import uuid
from typing import Dict
from starlette.responses import FileResponse, Response

API_BASE = "http://localhost:8000"

# mappa id -> (path, mime, filename) specifica per i preview dei servizi (evita conflitti con altri moduli)
_PREVIEW_FILES_SERVIZIO: Dict[str, dict] = {}


def documentazione_servizio_page_cliente(servizio_id: int):
    """Visualizza la documentazione associata al servizio (solo quella del servizio)"""
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto').style('background:#f0f0f0;border-radius:2.5em;max-width: 900px;display:flex;flex-direction:column;align-items:center;justify-content:center;'):
        ui.label('Documentazione del Servizio').classes('text-h5 q-mb-xl').style(
                'margin-top:5px;color:#1976d2;text-align:center;font-size:2.5em;font-weight:bold;margin-bottom:20px;margin-left:1em;margin-right:1em;'
            )
        doc_list = ui.column().classes('full-width').style('gap:20px;')

        resp = api_session.get(f'/documentazione/servizi/{servizio_id}/documenti')
        if resp.status_code == 200:
            docs = resp.json()
            if docs:
                for doc in docs:
                    with doc_list:
                        with ui.card().style('background:#f4f7fb;border-radius:1.5em;min-height:72px;padding:1em 2em;margin-bottom:8px;min-width:500px;margin-left:1.5em;margin-right:1.5em;'):
                            ui.label(doc.get('filename', 'Documento')).classes('text-body1 text-blue-grey-8')
                            with ui.row().classes('items-center').style('gap:8px;'):
                                ext = str(doc.get("filename", "")).split('.')[-1].lower()
                                # Visualizza (preview) solo per tipi visualizzabili
                                if ext in ["pdf", "jpg", "jpeg", "png"]:
                                    ui.button(
                                        'Visualizza',
                                        icon='visibility',
                                        color='info',
                                        on_click=lambda d=doc: _preview_documento_servizio(d)
                                    ).props('flat round type="button"')
                                # Scarica sempre disponibile
                                ui.button(
                                    'Scarica',
                                    icon='download',
                                    color='primary',
                                    on_click=lambda d=doc: _download_documento_servizio(d)
                                ).props('flat round type="button"')
            else:
                with doc_list:
                    ui.label('Nessun documento associato a questo servizio.').classes('text-grey-7 q-mt-md')
        else:
            with doc_list:
                ui.label('Errore nel recupero dei documenti').classes('text-negative')


def _download_documento_servizio(doc: dict):
    """
    Proxy server-side download:
    - chiama il backend usando api_session (server-side, include Authorization header)
    - riceve i bytes e salva in un file temporaneo sul server
    - chiama ui.download(path, filename) passando il path del file temporaneo
    - pianifica la rimozione del file temporaneo (cleanup) dopo un breve intervallo
    Questo evita preflight CORS e permette di scaricare direttamente il file senza aprirlo in una nuova tab.
    """
    try:
        content = api_session.download_documentazione(doc['id'])
    except Exception as e:
        ui.notify(f"Errore download: {e}", color='negative')
        return

    if not content:
        ui.notify("Errore: contenuto vuoto", color='negative')
        return

    # crea file temporaneo con estensione corretta (se possibile)
    filename = doc.get('filename') or f'documento_{doc["id"]}'
    suffix = ''
    if '.' in filename:
        suffix = os.path.splitext(filename)[1]

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
        # rimuovi file se qualcosa è andato storto
        if os.path.exists(tmp_file.name):
            try:
                os.unlink(tmp_file.name)
            except Exception:
                pass
        ui.notify(f"Errore salvataggio temporaneo: {e}", color='negative')
        return

    # Usa ui.download con il path del file temporaneo (NiceGUI si aspetta un path str)
    try:
        ui.download(tmp_file.name, filename)
    except Exception as e:
        ui.notify(f"Errore download client: {e}", color='negative')
        # cleanup immediato
        if os.path.exists(tmp_file.name):
            try:
                os.unlink(tmp_file.name)
            except Exception:
                pass
        return

    # Schedule cleanup del file temporaneo (es. dopo 60s)
    def _cleanup(path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    Timer(60.0, _cleanup, args=(tmp_file.name,)).start()


# --- Route raw + wrapper per i preview dei servizi (usa percorsi distinti per evitare conflitti) ---

@app.get('/__preview_servizio_raw/{preview_id}')
def _serve_preview_servizio_raw(preview_id: str):
    """Serve il file grezzo senza forzare Content-Disposition."""
    info = _PREVIEW_FILES_SERVIZIO.get(preview_id)
    if not info:
        return Response('Not found', status_code=404)
    path = info.get('path')
    mime = info.get('mime') or 'application/octet-stream'
    if not path or not os.path.exists(path):
        return Response('Not found', status_code=404)
    return FileResponse(path, media_type=mime)


@app.get('/__preview_servizio/{preview_id}')
def _serve_preview_servizio_wrapper(preview_id: str):
    """
    Pagina wrapper che mostra il file in iframe o img.
    Questo evita che il browser scarichi direttamente il file e ti dà controllo
    sul layout/resolution.
    """
    info = _PREVIEW_FILES_SERVIZIO.get(preview_id)
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
            <div class="controls"><a class="btn" href="/__preview_servizio_raw/{preview_id}" target="_blank" rel="noopener">Apri originale</a></div>
            <img src="/__preview_servizio_raw/{preview_id}" alt="preview">
          </body>
        </html>
        '''
    else:
        # PDF o altri: iframe con fullscreen controllato
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
              <a class="btn" href="/__preview_servizio_raw/{preview_id}" target="_blank" rel="noopener">Apri originale</a>
              <a class="btn" href="javascript:location.reload()">Ricarica</a>
            </div>
            <iframe src="/__preview_servizio_raw/{preview_id}"></iframe>
          </body>
        </html>
        '''
    return Response(html, media_type='text/html')


def _preview_documento_servizio(doc: dict):
    """
    Scarica i bytes dal backend, salva in file temporaneo e apre una nuova scheda
    che punta a /__preview_servizio/{preview_id} (wrapper HTML).
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
    _PREVIEW_FILES_SERVIZIO[preview_id] = {
        'path': tmp.name,
        'mime': mime,
        'filename': doc.get('filename') or f'doc_{doc["id"]}{suffix}'
    }

    # programma la cancellazione dopo 120 secondi (rimuove file e entry dalla mappa)
    def _cleanup(pid):
        info = _PREVIEW_FILES_SERVIZIO.pop(pid, None)
        if info:
            try:
                if os.path.exists(info['path']):
                    os.remove(info['path'])
            except Exception:
                pass

    Timer(120.0, _cleanup, args=(preview_id,)).start()

    # Apri nuova scheda verso il wrapper HTML che mostra il file dentro iframe/img
    try:
        ui.run_javascript(f"window.open('/__preview_servizio/{preview_id}', '_blank');")
    except Exception as e:
        ui.notify(f"Errore apertura nuova scheda: {e}", color='negative')
