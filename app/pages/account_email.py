from nicegui import ui
from app.api.api import api_session

def cambia_email_page():
    user = api_session.user
    if not user:
        ui.label("Utente non autenticato").classes("text-negative")
        return
    with ui.card().classes('glass-card shadow-7 q-mt-xl').style('max-width:440px;min-width:340px;padding:44px 0 44px 0;'):
        ui.label("Cambia email").classes('glass-title').style("font-size:1.5em;")
        nuova_email = ui.input("Nuova email").props("outlined dense type=email").classes("q-mt-md")
        password = ui.input("Password attuale", password=True).props("outlined dense").classes("q-mt-md")
        msg = ui.label().classes("q-mt-sm text-negative").style("min-height:1.4em")
        def do_change():
            msg.text = ""
            if not nuova_email.value or not password.value:
                msg.text = "Compila tutti i campi."
                return
            data = {"email": user.get("email"), "new_email": nuova_email.value, "password": password.value}
            try:
                resp = api_session.post("/auth/change-email", data)
                if resp.status_code == 200:
                    ui.notify("Email cambiata!", color="positive")
                    # Aggiorna utente in sessione
                    api_session.set_user({**user, "email": nuova_email.value})
                else:
                    msg.text = resp.json().get("detail", "Errore cambio email")
            except Exception:
                msg.text = "Errore connessione server"
        ui.button("Aggiorna", on_click=do_change).classes("q-mt-md glass-btn full-width")