from nicegui import ui
from app.api.api import api_session

def cambia_email_page():
    user = api_session.user

    
    if not user:
        ui.label("Utente non autenticato").classes("text-negative")
        return

    ui.query('body').style('display:flex;justify-content:center;align-items:center;height:100vh;margin:0;')
    with ui.card().classes('glass-card shadow-7 q-mt-xl').style('background:#f0f0f0;border-radius:2.5em;max-width:440px;min-width:340px;padding:44px 0 44px 0;display:flex;flex-direction:column;align-items:center;justify-content:center;'):
        
        ui.label("Cambia email").classes('glass-title').style('color:#1976d2;text-align:center;font-size:2.5em;font-weight:bold;')
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
                   
                    api_session.set_user({**user, "email": nuova_email.value})
                else:
                    
                    msg.text = resp.json().get("detail", "Errore cambio email")
            except Exception:
                
                msg.text = "Errore connessione server"

        
        ui.button("Aggiorna", on_click=do_change).classes("q-mt-md glass-btn").style('background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;color:#fff !important;position:relative;display:flex;align-items:center;justify-content:center;'
                    'max-width:330px;min-width:280px;'
                    'margin-top:12px;border-radius:12px;border-radius:1.8em;')

# --- SUGGERIMENTI MODIFICHE ---
# - Per cambiare la grafica: agisci su classi, style inline, o CSS globale (vedi ui.add_head_html e file account.py)
# - Per cambiare comportamento: modifica la funzione do_change, aggiungi validazione, spinner, dialog, ecc.
# - Per aggiungere campi: inserisci nuovi ui.input o ui.select dove vuoi (vedi doc NiceGUI)
# - Le funzioni NiceGUI principali: ui.input, ui.button, ui.label, ui.card, ui.column, ui.row, ui.notify, ui.dialog, ui.add_head_html (per CSS), ui.add_body_html (HTML custom)
# - Per vedere esempi e playground, visita https://nicegui.io/documentation

# - Ricordate di commentare ogni blocco e ogni funzione per facilitare la collaborazione!