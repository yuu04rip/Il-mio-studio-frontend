from nicegui import ui
from app.api.api import api_session

def login_page():
    print("Rendering login page")
    with ui.element("div").classes("auth-absolute-center"):
        with ui.card().classes('auth-modern-card shadow-8').style('max-width:410px;min-width:320px;padding:0;overflow:hidden;'):
            with ui.column().classes('items-center').style('padding:0;'):
                ui.icon('login').style('font-size:3.0em;color:#1976d2;margin-top:38px;')
                ui.label('Accedi').classes('auth-modern-title').style('margin-top:8px;margin-bottom:15px;font-size:2.05em;font-weight:700;letter-spacing:0.04em;')
                ui.separator().style("width:100%;margin-bottom:20px;")
                with ui.column().classes('justify-center items-center').style('width:82%;gap:18px;'):
                    ruolo = ui.select(
                        options=['CLIENTE', 'DIPENDENTE', 'NOTAIO'],
                        label='Ruolo'
                    ).props('outlined dense').classes('auth-modern-input')
                    email = ui.input('Email').props('outlined dense type=email').classes('auth-modern-input')
                    password = ui.input('Password', password=True).props('outlined dense').classes('auth-modern-input')
                    codice_notarile_row = ui.row().classes('w-full justify-center')
                    with codice_notarile_row:
                        codice_notarile = ui.input('Codice notarile (solo per notai)').props('outlined dense type=number').classes('auth-modern-input')
                    codice_notarile_row.visible = False

                    msg = ui.label().classes('q-mt-sm text-negative').style('min-height:1.3em;')

                    def update_codice_notarile_visibility(e):
                        codice_notarile_row.visible = (ruolo.value == 'NOTAIO')
                    ruolo.on('update:model-value', update_codice_notarile_visibility)

                    def do_login():
                        msg.text = ""
                        data = {'email': email.value, 'password': password.value}
                        selected_ruolo = ruolo.value.upper() if ruolo.value else ''
                        if not data['email'] or not data['password'] or not selected_ruolo:
                            msg.text = "Compila tutti i campi obbligatori."
                            return
                        if selected_ruolo == 'NOTAIO':
                            if not codice_notarile.value:
                                msg.text = "Inserisci il codice notarile."
                                return
                            try:
                                data['codice_notarile'] = int(codice_notarile.value)
                            except Exception:
                                msg.text = "Codice notarile non valido."
                                return
                        data['ruolo'] = selected_ruolo
                        try:
                            resp = api_session.post('/auth/login',json=data)
                        except Exception:
                            msg.text = "Errore di connessione al server."
                            return
                        if resp.status_code == 200:
                            token = resp.json()['access_token']
                            api_session.set_token(token)
                            user_resp = api_session.get('/users/me')
                            if user_resp.status_code == 200:
                                api_session.set_user(user_resp.json())
                                ruolo_utente = api_session.user.get('ruolo', '').upper()
                                # PRIMA PRIMA: cliente_id = ???   <--- qui errore!
                                cliente_id = api_session.user.get('id', None)  # oppure 'cliente_id', dipende da come lo chiami nel backend
                                if ruolo_utente == 'CLIENTE' and cliente_id:
                                    ui.navigate.to(f'/home_cliente?cliente_id={cliente_id}')
                                elif ruolo_utente == 'DIPENDENTE':
                                    ui.navigate.to('/home_dipendente')
                                elif ruolo_utente == 'NOTAIO':
                                    ui.navigate.to('/home_notaio')
                                else:
                                    msg.text = "Ruolo utente non riconosciuto."
                            else:
                                msg.text = "Errore nel recupero dati utente."
                        elif resp.status_code == 403:
                            msg.text = "Hai messo il ruolo errato."
                        else:
                            try:
                                msg.text = resp.json().get('detail', 'Email o password non valide.')
                            except Exception:
                                msg.text = 'Email o password non valide.'

                    ui.button('Accedi', on_click=do_login).classes('auth-modern-btn q-mt-lg')
                    ui.button('Registrati', on_click=lambda: ui.navigate.to('/register')).props('flat').classes('auth-modern-link')
                    ui.button('Password dimenticata?', on_click=lambda: ui.navigate.to('/change_password')).props('flat color=primary').classes('auth-modern-link')
                ui.separator().style("width:100%;margin-top:28px;")
                ui.label("© 2025 Il Mio Studio").style("color:#b0b7c3;margin:23px 0 10px 0;font-size:.98em;")

def register_page():
    with ui.element("div").classes("auth-absolute-center"):
        with ui.card().classes('auth-modern-card shadow-8').style('max-width:410px;min-width:320px;padding:0;overflow:hidden;'):
            with ui.column().classes('items-center').style('padding:0;'):
                ui.icon('person_add').style('font-size:3.0em;color:#1976d2;margin-top:38px;')
                ui.label('Registrati').classes('auth-modern-title').style('margin-top:8px;margin-bottom:15px;font-size:2.05em;font-weight:700;letter-spacing:0.04em;')
                ui.separator().style("width:100%;margin-bottom:20px;")
                with ui.column().classes('justify-center items-center').style('width:82%;gap:18px;'):
                    nome = ui.input('Nome').props('outlined dense').classes('auth-modern-input')
                    cognome = ui.input('Cognome').props('outlined dense').classes('auth-modern-input')
                    email = ui.input('Email').props('outlined dense type=email').classes('auth-modern-input')
                    numero = ui.input('Numero telefonico').props('outlined dense type=tel').classes('auth-modern-input')
                    password = ui.input('Password', password=True).props('outlined dense').classes('auth-modern-input')
                    msg = ui.label().classes('q-mt-sm text-negative').style('min-height:1.3em;')
                    def do_register():
                        msg.text = ""
                        data = {
                            'nome': nome.value,
                            'cognome': cognome.value,
                            'email': email.value,
                            'numeroTelefonico': numero.value if numero.value else None,
                            'password': password.value,
                            'ruolo': 'CLIENTE',
                        }
                        if not data['nome'] or not data['cognome'] or not data['email'] or not data['password']:
                            msg.text = "Compila tutti i campi obbligatori."
                            return
                        try:
                            resp = api_session.post('/auth/register', data)
                        except Exception:
                            msg.text = "Errore di connessione al server"
                            return
                        if resp.status_code == 200:
                            # Login automatico dopo registrazione
                            login_data = {
                                'email': email.value,
                                'password': password.value,
                            }
                            try:
                                login_resp = api_session.post('/auth/login', login_data)
                                if login_resp.status_code == 200:
                                    token = login_resp.json()['access_token']
                                    api_session.set_token(token)
                                    user_resp = api_session.get('/users/me')
                                    if user_resp.status_code == 200:
                                        api_session.set_user(user_resp.json())
                                        ui.navigate.to('/home_cliente')
                                        return
                                msg.text = "Registrazione riuscita, ma errore nel login automatico."
                            except Exception:
                                msg.text = "Registrazione riuscita, ma errore nel login automatico."
                        else:
                            try:
                                msg.text = resp.json().get('detail', 'Errore in registrazione')
                            except Exception:
                                msg.text = 'Errore in registrazione'
                    ui.button('Registrati', on_click=do_register).classes('auth-modern-btn q-mt-lg')
                    ui.button('Torna al login', on_click=lambda: ui.navigate.to('/')).props('flat').classes('auth-modern-link')
                ui.separator().style("width:100%;margin-top:28px;")
                ui.label("© 2025 Il Mio Studio").style("color:#b0b7c3;margin:23px 0 10px 0;font-size:.98em;")


def change_password_page():
    with ui.element("div").classes("auth-absolute-center"):
        with ui.card().classes('auth-modern-card shadow-8').style('max-width:410px;min-width:320px;padding:0;overflow:hidden;'):
            with ui.column().classes('items-center').style('padding:0;'):
                ui.icon('vpn_key').style('font-size:3.0em;color:#1976d2;margin-top:38px;')
                ui.label('Recupero/Cambio password').classes('auth-modern-title').style('margin-top:8px;margin-bottom:15px;font-size:1.55em;font-weight:700;letter-spacing:0.04em;')
                ui.separator().style("width:100%;margin-bottom:20px;")
                with ui.column().classes('justify-center items-center').style('width:82%;gap:18px;'):
                    email = ui.input('Email').props('outlined dense type=email').classes('auth-modern-input')
                    old_pwd = ui.input('Password attuale', password=True).props('outlined dense').classes('auth-modern-input')
                    new_pwd = ui.input('Nuova password', password=True).props('outlined dense').classes('auth-modern-input')
                    codice_notarile = ui.input('Codice notarile (solo per notai)').props('outlined dense type=number').classes('auth-modern-input')
                    msg = ui.label().classes('q-mt-sm text-negative').style('min-height:1.3em;')
                    def do_change():
                        msg.text = ""
                        data = {
                            'email': email.value,
                            'old_password': old_pwd.value,
                            'new_password': new_pwd.value,
                            'codice_notarile': int(codice_notarile.value) if codice_notarile.value else None,
                        }
                        if not data['email'] or not data['old_password'] or not data['new_password']:
                            msg.text = "Compila tutti i campi richiesti."
                            return
                        try:
                            resp = api_session.post('/auth/change-password', data)
                            if resp.status_code == 200:
                                msg.text = "Password cambiata!"
                                msg.classes('text-positive')
                            else:
                                try:
                                    msg.text = resp.json().get("detail", "Errore aggiornamento password")
                                except Exception:
                                    msg.text = "Errore aggiornamento password"
                        except Exception:
                            msg.text = "Errore di connessione al server"
                    ui.button('Cambia password', on_click=do_change).classes('auth-modern-btn q-mt-lg')
                    ui.button('Torna al login', on_click=lambda: ui.navigate.to('/')).props('flat').classes('auth-modern-link')
                ui.separator().style("width:100%;margin-top:28px;")
                ui.label("© 2025 Il Mio Studio").style("color:#b0b7c3;margin:23px 0 10px 0;font-size:.98em;")


# --- Stili globali per tutte le card di autenticazione ---
ui.add_head_html("""
<style>
html, body {
    height: 100%;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
body { background: linear-gradient(107deg, #fafdff 0%, #e5eefc 100%); }
.auth-absolute-center {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: none;
    z-index: 10;
}
.auth-modern-card {
    background: rgba(255,255,255,0.95) !important;
    box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important;
    border-radius: 2.5em !important;
    border: 1.7px solid #e3eaf1 !important;
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    overflow: hidden;
    margin: auto;
    max-width: 410px;
    width: 100%;
}
.auth-modern-title {
    background: none !important;
    color: #1976d2 !important;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-align: center;
    margin-top: 0;
    margin-bottom: 11px;
    width: fit-content;
    display: block;
}
.auth-modern-input input, .auth-modern-input .q-field__native {
    background: #f7fafd !important;
    border-radius: 1.25em !important;
    font-size:1.09em;
    min-height:44px;
    border: 1.2px solid #e3eaf1 !important;
    box-shadow: none !important;
}
.auth-modern-input input:focus, .auth-modern-input .q-field__native:focus {
    border: 1.2px solid #1976d2 !important;
}
.auth-modern-btn {
    font-size: 1.12em !important;
    font-weight: 600;
    border-radius: 1.8em !important;
    background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px 0 #2196f341;
    padding: 0.95em 0 !important;
    margin-top: 10px;
    width: 100%;
    transition: background .17s, box-shadow .16s, transform .14s;
    border: none !important;
}
.auth-modern-btn:hover, .auth-modern-btn:focus {
    background: linear-gradient(90deg, #1976d2 50%, #2196f3 100%) !important;
    color: #fff !important;
    box-shadow: 0 6px 22px 0 #1976d249;
    outline: none;
    transform: scale(1.035);
}
.auth-modern-link {
    font-size:1.04em !important;
    color: #1976d2 !important;
    font-weight: 500;
    text-align: center;
    border-radius: 2.2em;
    background: transparent !important;
    margin-top: 2px;
    margin-bottom: 2px;
    width: 100% !important;
    transition: color .13s, background .13s;
}
.auth-modern-link:hover {
    text-decoration: underline !important;
    color: #0d47a1 !important;
    background: #e3f1fd !important;
}
</style>
""")