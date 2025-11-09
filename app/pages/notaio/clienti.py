from nicegui import ui
from app.api.api import api_session

SEARCH_MIN_LENGTH = 2  # soglia minima per attivare il filtro

def clienti_page():
    ui.label('Clienti').classes('text-h5 q-mt-xl q-mb-lg').style(
        'background:#1976d2;color:white;border-radius:2em;padding:.5em 2.5em;display:block;text-align:center;font-weight:600;letter-spacing:0.04em;'
    )

    search = ui.input('', placeholder="Cerca per nome o cognome...").props('outlined dense').style('max-width:220px;margin-bottom:18px;')
    clienti_list = ui.column().classes('full-width').style('gap:18px;')

    clienti_originali = []
    clienti_display = []

    def carica_clienti():
        nonlocal clienti_originali
        try:
            resp = api_session.get('/studio/clienti/')
            clienti_originali = resp.json() if resp.status_code == 200 else []
        except Exception as e:
            clienti_originali = []
            print(f"Errore caricamento clienti: {e}")
        mostra_tutti_clienti()

    def mostra_tutti_clienti():
        clienti_display[:] = clienti_originali[:]
        render_clienti()

    def filtra_clienti(testo_ricerca):
        testo = testo_ricerca.strip().lower()
        if not testo or len(testo) < SEARCH_MIN_LENGTH:
            mostra_tutti_clienti()
            return

        tokens = [t for t in testo.split() if t]

        def match(cli):
            nome = cli.get('utente', {}).get('nome', '')
            cognome = cli.get('utente', {}).get('cognome', '')
            email = cli.get('utente', {}).get('email', '')
            fields = ' '.join([str(nome), str(cognome), str(email)]).lower()
            words = fields.split()
            for token in tokens:
                if not any(w.startswith(token) for w in words):
                    return False
            return True

        clienti_display[:] = [c for c in clienti_originali if match(c)]
        render_clienti()

    def render_clienti():
        clienti_list.clear()
        if not clienti_display:
            with clienti_list:
                ui.label('Nessun cliente trovato.').classes('text-grey-7 q-mt-md')
            return

        for cli in clienti_display:
            with clienti_list:
                with ui.card().style('background:#e3f2fd;border-radius:1em;min-height:78px;padding:1em 2em;'):
                    nome = cli.get('utente', {}).get('nome', '')
                    cognome = cli.get('utente', {}).get('cognome', '')
                    ui.label(f"{nome} {cognome}").classes('text-body1 q-mb-xs')
                    with ui.row().style('gap:8px;'):
                        ui.button(
                            'Servizi',
                            icon='work',
                            color='primary',
                            on_click=lambda id=cli['id']: visualizza_servizi(id)
                        ).props('flat round')
                        ui.button(
                            'Documenti',
                            icon='folder',
                            color='accent',
                            on_click=lambda id=cli['id']: visualizza_documenti(id)
                        ).props('flat round')

    def visualizza_servizi(cliente_id):
        ui.navigate.to(f'/accettazione')

    def visualizza_documenti(servizio_id):
        ui.navigate.to(f'/servizi/{servizio_id}/documenti')

    def on_search_change(e=None):
        val = search.value if search.value is not None else ''
        val = str(val).strip()
        if val == '' or len(val) < SEARCH_MIN_LENGTH:
            mostra_tutti_clienti()
        else:
            filtra_clienti(val)

    search.on('update:model-value', on_search_change)
    carica_clienti()
