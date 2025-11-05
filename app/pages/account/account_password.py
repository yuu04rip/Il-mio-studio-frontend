from nicegui import ui
from app.api.api import api_session

def cambia_password_page():
    user = api_session.user
    if not user:
        ui.label("Utente non autenticato").classes("text-negative")
        return
    ui.query('body').style('display:flex;justify-content:center;align-items:center;height:100vh;margin:0;')
    with ui.card().classes('glass-card shadow-7 q-mt-xl').style('border-radius:2.5em;background:#f0f0f0;max-width:440px;min-width:340px;padding:44px 0 44px 0;display:flex;flex-direction:column;align-items:center;justify-content:center;'):
        ui.label("Cambia password").classes('glass-title').style('color:#1976d2;text-align:center;font-size:2.5em;font-weight:bold;margin-left:10px;margin-right:10px;')
        old_pwd = ui.input("Password attuale", password=True).props("outlined dense").classes("q-mt-md")
        new_pwd = ui.input("Nuova password", password=True).props("outlined dense").classes("q-mt-md")
        msg = ui.label().classes("q-mt-sm text-negative").style("min-height:1.4em")
        def do_change():
            msg.text = ""
            if not old_pwd.value or not new_pwd.value:
                msg.text = "Compila tutti i campi."
                return
            data = {"email": user.get("email"), "old_password": old_pwd.value, "new_password": new_pwd.value}
            try:
                resp = api_session.post("/auth/change-password", data)
                if resp.status_code == 200:
                    ui.notify("Password cambiata!", color="positive")
                else:
                    msg.text = resp.json().get("detail", "Errore cambio password")
            except Exception:
                msg.text = "Errore connessione server"
        ui.button("Cambia password", on_click=do_change).style('background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;color:#fff !important;position:relative;display:flex;align-items:center;justify-content:center;'
                    'max-width:330px;min-width:280px;'
                    'margin-top:12px;border-radius:12px;border-radius:1.8em;')