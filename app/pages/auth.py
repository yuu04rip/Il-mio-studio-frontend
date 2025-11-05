from nicegui import ui
from app.api.api import api_session


def login_page():
     ui.add_head_html('<link rel="stylesheet" href="/static/styles.css">')
     with ui.column().classes('items-center justify-center w-full').style('display:flex;height:100vh;'):
        with ui.card().classes('auth-modern-card shadow-8').style('max-width:420px;min-width:320px;padding:0;overflow:hidden;align-items:center;'):
            with ui.column().classes('items-center').style('padding:0;'):
                ui.icon('login').style('font-size:3.0em;color:#1976d2;margin-top:30px;')
                ui.label('Accedi').classes('auth-modern-title').style('margin-top:8px;margin-bottom:15px;font-size:2.05em;font-weight:700;letter-spacing:0.04em;')
                ui.separator().style("width:100%;margin-bottom:20px;")
                with ui.column().classes('justify-center items-center').style('width:82%;gap:18px;'):
                    ruolo = ui.select(
                        options=['CLIENTE', 'DIPENDENTE', 'NOTAIO'],
                        label='Ruolo'
                    ).props('outlined dense').classes('auth-modern-input').style("align-self:flex-start;")
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
                            resp = api_session.post('/auth/login', json=data)
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
                                cliente_id = api_session.user.get('id', None)
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
     ui.add_head_html('<link rel="stylesheet" href="/static/styles.css">')
     with ui.column().classes('items-center justify-center w-full').style('display:flex;height:100vh;'):
        with ui.card().classes('auth-modern-card shadow-8').style('max-width:410px;min-width:320px;padding:0;overflow:hidden;align-items:center;'):
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
    ui.add_head_html('<link rel="stylesheet" href="/static/styles.css">')
    with ui.column().classes('items-center justify-center w-full').style('display:flex;height:100vh;'):
        with ui.card().classes('auth-modern-card shadow-8').style('max-width:410px;min-width:320px;padding:0;overflow:hidden;align-items:center;'):
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


