from nicegui import ui
from app.api.api import api_session

def cambia_email_page():
    user = api_session.user

    # --- Sezione controllo autenticazione ---
    # Qui puoi modificare il messaggio d'errore o aggiungere grafica custom se l'utente non è loggato
    if not user:
        ui.label("Utente non autenticato").classes("text-negative")
        return

    # --- Card principale per la modifica email ---
    # Puoi agire su classi, style, colori per cambiare il look
    with ui.card().classes('glass-card shadow-7 q-mt-xl').style('max-width:440px;min-width:340px;padding:44px 0 44px 0;'):
        # --- Titolo della card ---
        # Cambia font-size, colore, background qui o in CSS (vedi file account.py per esempio)
        ui.label("Cambia email").classes('glass-title').style("font-size:1.5em;")
        # --- Input email nuova ---
        # Puoi aggiungere props (color, placeholder, etc), cambiare style/classi, aggiungere icone
        nuova_email = ui.input("Nuova email").props("outlined dense type=email").classes("q-mt-md")
        # --- Input password attuale ---
        # Puoi aggiungere validazione lato client, icone, suggerimenti
        password = ui.input("Password attuale", password=True).props("outlined dense").classes("q-mt-md")
        # --- Label messaggio errore/successo ---
        # Cambia min-height per look, aggiungi classi per colori diversi
        msg = ui.label().classes("q-mt-sm text-negative").style("min-height:1.4em")

        # --- Funzione chiamata al click su "Aggiorna" ---
        # Qui puoi aggiungere logica di validazione, feedback visuale, spinner, popup ecc.
        def do_change():
            msg.text = ""
            # --- Controllo campi obbligatori ---
            if not nuova_email.value or not password.value:
                msg.text = "Compila tutti i campi."
                return
            # --- Prepara dati per API ---
            data = {"email": user.get("email"), "new_email": nuova_email.value, "password": password.value}
            try:
                # --- Chiamata API NiceGUI ---
                # Puoi vedere come si usa api_session.post (vedi doc: https://nicegui.io/documentation)
                resp = api_session.post("/auth/change-email", data)
                if resp.status_code == 200:
                    # --- Notifica successo ---
                    # ui.notify mostra popup in alto, puoi cambiare colore/durata
                    ui.notify("Email cambiata!", color="positive")
                    # --- Aggiorna dati utente in sessione ---
                    api_session.set_user({**user, "email": nuova_email.value})
                else:
                    # --- Mostra errore tornato dal backend ---
                    msg.text = resp.json().get("detail", "Errore cambio email")
            except Exception:
                # --- Mostra errore di connessione ---
                msg.text = "Errore connessione server"

        # --- Bottone Aggiorna ---
        # Puoi cambiare colore, icona, props, classi per look diverso
        ui.button("Aggiorna", on_click=do_change).classes("q-mt-md glass-btn full-width")

# --- SUGGERIMENTI MODIFICHE ---
# - Per cambiare la grafica: agisci su classi, style inline, o CSS globale (vedi ui.add_head_html e file account.py)
# - Per cambiare comportamento: modifica la funzione do_change, aggiungi validazione, spinner, dialog, ecc.
# - Per aggiungere campi: inserisci nuovi ui.input o ui.select dove vuoi (vedi doc NiceGUI)
# - Le funzioni NiceGUI principali: ui.input, ui.button, ui.label, ui.card, ui.column, ui.row, ui.notify, ui.dialog, ui.add_head_html (per CSS), ui.add_body_html (HTML custom)
# - Per vedere esempi e playground, visita https://nicegui.io/documentation

# - Ricordate di commentare ogni blocco e ogni funzione per facilitare la collaborazione!