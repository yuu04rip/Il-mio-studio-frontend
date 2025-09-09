from nicegui import ui
from app.api.api import api_session
from app.components.components import header

def accettazione_servizi_page():
    header("Accettazione Servizi")
    res = api_session.get('/servizi/da_accettare')
    if res.status_code == 200:
        servizi = res.json()
        for servizio in servizi:
            with ui.card().classes('q-mb-md'):
                ui.label(f"Servizio: {servizio['tipo']}")
                ui.label(f"Cliente: {servizio['cliente_nome']}")
                ui.button('Accetta', on_click=lambda s=servizio: accetta_servizio(s['id'])).props('color=positive')
    else:
        ui.label("Nessun servizio da accettare.")

def accetta_servizio(servizio_id):
    res = api_session.post(f"/servizi/{servizio_id}/accetta", {})
    if res.status_code == 200:
        ui.notify("Servizio accettato!")
        ui.open('/accettazione')
    else:
        ui.notify("Errore accettazione servizio.")