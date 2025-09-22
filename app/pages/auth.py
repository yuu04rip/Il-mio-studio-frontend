from nicegui import ui
from app.api.api import api_session

def login_page():
    with ui.element("div").classes("auth-absolute-center"):
        with ui.card().classes('auth-modern-card').style('position:relative;'):
            with ui.column().classes('items-center').style('width:100%;gap:14px;'):
                email = ui.input('Email').props('outlined dense type=email').classes('auth-modern-input')
                password = ui.input('Password', password=True).props('outlined dense').classes('auth-modern-input')
                ruolo = ui.select(
                    options=['CLIENTE', 'DIPENDENTE', 'NOTAIO'],
                    label='Ruolo'
                ).props('outlined dense').classes('auth-modern-input')
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

                ui.button('Accedi', on_click=do_login).classes('auth-modern-btn')
                ui.button('Registrati', on_click=lambda: ui.navigate.to('/register')).classes('auth-modern-secondary')
                ui.button('Credenziali Dimenticate', on_click=lambda: ui.navigate.to('/change_password')).classes('auth-modern-link')

def register_page():
    with ui.element("div").classes("auth-absolute-center"):
        with ui.card().classes('auth-modern-card').style('position:relative;'):
            with ui.column().classes('items-center').style('width:100%;gap:14px;'):
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

                ui.button('Registrati', on_click=do_register).classes('auth-modern-btn')
                ui.button('Torna al login', on_click=lambda: ui.navigate.to('/')).classes('auth-modern-secondary')

def change_password_page():
    with ui.element("div").classes("auth-absolute-center"):
        with ui.card().classes('auth-modern-card').style('position:relative;'):
            with ui.column().classes('items-center').style('width:100%;gap:14px;'):
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

                ui.button('Cambia password', on_click=do_change).classes('auth-modern-btn')
                ui.button('Torna al login', on_click=lambda: ui.navigate.to('/')).classes('auth-modern-secondary')

ui.add_head_html("""
<style>
html, body {
    height: 100%;
    margin: 0;
    padding: 0;
    background: #ffffff; /* sfondo bianco */
    font-family: 'Segoe UI', 'Roboto', sans-serif;
}

/* Contenitore */
.auth-absolute-center {
    position: fixed;
    inset: 0;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Card larga orizzontale */
.auth-modern-card {
    background: #40BFFF !important; /* azzurro acceso */
    border-radius: 1.8em !important;
    padding: 50px 40px !important;
    width: 650px;   /* più largo per desktop */
    min-height: 350px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

/* Icona utente sopra la card */
.auth-modern-card::before {
    content: '';
    display: block;
    position: absolute;
    top: -75px;
    left: 50%;
    transform: translateX(-50%);
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background: #001F80 url('https://img.icons8.com/ios-filled/100/ffffff/user.png') no-repeat center;
    background-size: 55%;
}

/* Input + bottoni = stessa forma */
.auth-modern-input input, 
.auth-modern-input .q-field__native,
.auth-modern-btn, 
.auth-modern-secondary {
    border-radius: 2em !important;
    width: 100%;
    min-height: 44px;
}

/* Input */
.auth-modern-input input {
    background: #fff !important;
    border: 1px solid #ccc !important;
    padding-left: 42px; /* spazio per icona */
    font-size: 1em;
}

/* Icone dentro gli input */
.input-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.2em;
    color: #555;
}

/* Bottone principale */
.auth-modern-btn {
    font-size: 1.05em !important;
    font-weight: 600;
    background: #001F80 !important;
    color: #fff !important;
    border: none !important;
    margin-top: 12px;
}
.auth-modern-btn:hover {
    background: #0a2fa1 !important;
}

/* Bottone secondario */
.auth-modern-secondary {
    background: #001F80 !important;
    color: #fff !important;
    margin-top: 6px;
}
.auth-modern-secondary:hover {
    background: #0a2fa1 !important;
}

/* Link */
.auth-modern-link {
    font-size: 0.9em !important;
    color: #ffffff !important;
    margin-top: 8px;
}
.auth-modern-link:hover {
    text-decoration: underline !important;
    color: #e0e0ff !important;
}
</style>
""")
