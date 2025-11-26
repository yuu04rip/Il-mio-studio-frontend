from nicegui import ui
from app.api.api import api_session

def dipendenti_page():
    ui.add_head_html("""
<style>
.custom-btn.q-btn{
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
</style>
""")
    with ui.card().classes('q-mb-xl shadow-3').style(
            'background: rgba(240,240,240) !important;'
            'box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important;'
            'border-radius: 2.5em !important;border: 1.7px solid #e3eaf1 !important;'
            'backdrop-filter: blur(6px);-webkit-backdrop-filter: blur(6px);overflow: hidden;'
            'margin: auto;align-items:center;max-width: 350px;width: 100%;'
    ):
        ui.label('Aggiungi Dipendente').classes('text-h6 q-mb-md').style(
            'background: transparent;color:#1976d2;border-radius:2em;padding:.6em 2.5em;'
            'display:block;text-align:center;font-weight:600;letter-spacing:0.04em;font-size:2rem;'
        )
        nome = ui.input('Nome').props('outlined dense').style('max-width: 300px; width: 100%;')
        cognome = ui.input('Cognome').props('outlined dense').style('max-width: 300px; width: 100%;')
        email = ui.input('Email').props('outlined dense type=email').style('max-width: 300px; width: 100%;')
        numero = ui.input('Numero telefonico').props('outlined dense type=tel').style('max-width: 300px; width: 100%;')
        password = ui.input('Password (facoltativa)').props('outlined dense').style('max-width: 300px; width: 100%;')

        # ruolo: mostra la select principale (DIPENDENTE / NOTAIO)
        ruolo = ui.select(
            options=['DIPENDENTE', 'NOTAIO'],
            label='Ruolo',
        ).props('outlined dense').classes('q-mt-sm')
        # sotto-ruolo (tipo dipendente) visibile solo se ruolo == DIPENDENTE
        tipo_select = ui.select(
            options=['CONTABILE', 'ASSISTENTE'],
            label='Tipo dipendente (opzionale)',
        ).props('outlined dense').classes('q-mt-sm')
        # nascondi inizialmente
        tipo_select.visible = False

        # handler per mostrare/nascondere il tipo quando ruolo cambia
        def _on_ruolo_change(e=None):
            val = ruolo.value or ''
            tipo_select.visible = (str(val).upper() == 'DIPENDENTE')
            if not tipo_select.visible:
                tipo_select.value = None

        ruolo.on('update:model-value', _on_ruolo_change)

        msg = ui.label().classes('text-negative q-mt-sm')

        def do_add():
            msg.text = ""
            data = {
                'nome': nome.value,
                'cognome': cognome.value,
                'email': email.value,
                'numeroTelefonico': numero.value,
                # password facoltativa: se vuota il backend genererà una password temporanea
                'password': password.value or None,
                # ruolo (backend si aspetta 'ruolo' nella richiesta di registrazione generale)
                'ruolo': (ruolo.value or 'DIPENDENTE').lower(),
            }

            # se abbiamo selezionato sottotipo per DIPENDENTE, includilo come 'tipo'
            if (ruolo.value or '').upper() == 'DIPENDENTE' and tipo_select.value:
                # mappa ad enum stringa attesa dal backend (minuscole)
                data['tipo'] = tipo_select.value.lower()

            if not all([data['nome'], data['cognome'], data['email']]):
                msg.text = "Compila tutti i campi obbligatori (nome, cognome, email)."
                return
            try:
                if (ruolo.value or '').upper() == "DIPENDENTE":
                    # api_session.register_dipendente dovrebbe inviare la richiesta al backend
                    resp = api_session.register_dipendente(data)
                    # api_session may return a response-like or dict; handle both
                    if hasattr(resp, 'status_code') and getattr(resp, 'status_code') in (200, 201):
                        ui.notify('Dipendente aggiunto! Credenziali inviate via email (se l\'invio è andato a buon fine).', color='positive')
                    elif isinstance(resp, dict):
                        ui.notify('Dipendente aggiunto! Credenziali inviate via email (se l\'invio è andato a buon fine).', color='positive')
                    else:
                        ui.notify('Risposta inaspettata dal server ma creazione eseguita.', color='warning')

                    # pulizia campi UI locali
                    nome.value = ''
                    cognome.value = ''
                    email.value = ''
                    numero.value = ''
                    password.value = ''
                    tipo_select.value = None
                    tipo_select.visible = False
                    ruolo.value = 'DIPENDENTE'

                    # ricarica intera pagina per evitare il bug di stato residuo
                    # piccolo delay per far vedere la notifica prima del reload
                    ui.run_javascript("window.setTimeout(() => location.reload(), 600);")
                elif (ruolo.value or '').upper() == "NOTAIO":
                    msg.text = "Registrazione notai non supportata qui. Usa la sezione dedicata."
                else:
                    msg.text = "Ruolo non valido."
            except Exception as e:
                msg.text = f"Errore: {str(e)}"

        ui.button('Aggiungi', on_click=do_add).classes('custom-btn')

    with ui.card().classes('shadow-5').style(
            'background:#E0F7FA !important;box-shadow: 0 10px 32px 0 #1976d222, 0 2px 10px 0 #00000012 !important;'
            'border-radius: 1em !important;border: 1.7px solid #e3eaf1 !important;'
            'backdrop-filter: blur(6px);-webkit-backdrop-filter: blur(6px);overflow: hidden;'
            'margin: auto;align-items:center;max-width: 350px;width: 100%;'
    ):
        ui.label('Lista Dipendenti').classes('text-h6 q-mb-md')
        dip_list = ui.column().classes('full-width').style('gap:14px;')

        def refresh_dipendenti():
            dip_list.clear()
            try:
                resp = api_session.get('/studio/dipendenti/')
                if getattr(resp, 'status_code', None) == 200:
                    for dip in resp.json():
                        with dip_list:
                            with ui.row().style('align-items:center;gap:18px;'):
                                ruolo_display = dip['utente'].get('ruolo', '')
                                # Mostra anche il tipo del dipendente se presente
                                tipo_display = dip.get('tipo') or dip.get('tipoDipendente') or ''
                                label_text = f"{dip['utente']['nome']} {dip['utente']['cognome']} ({ruolo_display.capitalize()})"
                                if tipo_display:
                                    label_text = f"{label_text} - {str(tipo_display).capitalize()}"
                                ui.label(label_text).classes('text-body1')
                                ui.button('Elimina', icon='delete', color='negative', on_click=lambda id=dip['id']: elimina_dipendente(id)).props('flat round')
                else:
                    ui.label('Impossibile caricare la lista dipendenti.').classes('text-negative')
            except Exception:
                ui.label('Errore di connessione').classes('text-negative')

        def elimina_dipendente(dipendente_id):
            try:
                resp = api_session.delete(f"/studio/dipendente/{dipendente_id}/distruggi")
                if getattr(resp, 'status_code', None) == 200:
                    ui.notify('Dipendente eliminato!', color='positive')
                else:
                    ui.notify('Errore eliminazione', color='negative')
            except Exception:
                ui.notify('Errore di connessione', color='negative')
            refresh_dipendenti()

        refresh_dipendenti()