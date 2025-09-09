from nicegui import ui
from app.api.api import api_session
from app.components.components import header

def documentazione_cliente_page():
    header("Documentazione personale")
    # 1. Recupera id cliente (qui esempio: da sessione utente)
    user = api_session.user
    cliente_id = user.get('id') if user else None
    if not cliente_id:
        ui.label("Utente non autenticato").classes('text-negative')
        return

    # 2. Ottieni i documenti dal backend
    res = api_session.get(f'/documentazione/visualizza/{cliente_id}')
    if res.status_code == 200:
        docs = res.json()
        if docs:
            for doc in docs:
                with ui.row().classes('q-pa-md'):
                    ui.label(f"{doc['tipo']}: {doc['filename']}")
                    ui.button('Scarica', icon='download', on_click=lambda d=doc: download_documento(d['id']))
                    ui.button('Elimina', icon='delete', on_click=lambda d=doc: elimina_documento(d['id'], cliente_id))
                    ui.button('Sostituisci', icon='upload', on_click=lambda d=doc: sostituisci_documento(d['id'], cliente_id))
        else:
            ui.label("Nessun documento caricato.")
    else:
        ui.label("Errore nel recupero dei documenti.").classes('text-negative')
    # 3. Upload nuovo documento
    with ui.row().classes('q-mt-lg'):
        tipo_doc = ui.select(
            ["CARTA_IDENTITA", "PASSAPORTO", "TESSERA_SANITARIA", "PATENTE"],
            label='Tipo Documento'
        )
        ui.upload(
            label='Carica nuovo documento',
            auto_upload=True,
            on_upload=lambda e: upload_documento(e, cliente_id, tipo_doc.value)
        ).props('accept=.pdf,.jpg,.jpeg,.png')

def upload_documento(event, cliente_id, tipo):
    if not tipo:
        ui.notify("Seleziona il tipo di documento!")
        return
    file = event.files[0]
    # POST multipart/form-data a /documentazione/carica
    with open(file['content'], "rb") as f:
        files = {'file': (file['name'], f, file['type'])}
        data = {'cliente_id': str(cliente_id), 'tipo': tipo}
        resp = api_session.post('/documentazione/carica', data=data, files=files)
    if resp.status_code == 200:
        ui.notify("Documento caricato!")
        ui.open('/documentazione')
    else:
        ui.notify("Errore nel caricamento.")

def download_documento(doc_id):
    # Implementa qui la chiamata reale di download dal backend (es: /documentazione/download/{doc_id})
    ui.notify(f"Scarica documento {doc_id} (implementare download reale)")

def elimina_documento(doc_id, cliente_id):
    res = api_session.delete(f"/documentazione/{doc_id}")
    if res.status_code == 200:
        ui.notify("Documento eliminato!")
        ui.open(f'/documentazione')
    else:
        ui.notify("Errore eliminazione.")

def sostituisci_documento(doc_id, cliente_id):
    def on_upload(event):
        file = event.files[0]
        with open(file['content'], "rb") as f:
            files = {'file': (file['name'], f, file['type'])}
            resp = api_session.put(f'/documentazione/sostituisci/{doc_id}', files=files)
        if resp.status_code == 200:
            ui.notify("Documento sostituito!")
            ui.open('/documentazione')
        else:
            ui.notify("Errore nella sostituzione.")
    ui.upload(label='Sostituisci documento', auto_upload=True, on_upload=on_upload).props('accept=.pdf,.jpg,.jpeg,.png')
