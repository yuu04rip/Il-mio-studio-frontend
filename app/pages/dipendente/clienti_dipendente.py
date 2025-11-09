from nicegui import ui
from app.api.api import api_session

SEARCH_MIN_LENGTH = 2  # soglia minima per attivare il filtro


def clienti_page_dipendente():
    ui.label('Clienti').classes('text-h5 q-mt-xl q-mb-lg').style(
        'background:#1976d2;color:white;border-radius:2em;padding:.5em 2.5em;display:block;text-align:center;font-weight:600;letter-spacing:0.04em;'
    )

    # mostra il nome del dipendente (se disponibile in api_session.user)
    user = getattr(api_session, 'user', None) or {}
    user_nome = user.get('nome') or user.get('username') or ''
    user_cognome = user.get('cognome') or ''
    if user_nome or user_cognome:
        ui.label(f'Operatore: {user_nome} {user_cognome}').classes('text-subtitle2 q-mb-sm')

    # barra di ricerca + checkbox "solo i miei"
    row = ui.row().classes('items-center q-mb-md').style('gap:12px;')
    with row:
        search = ui.input('', placeholder="Cerca per nome o cognome...").props('outlined dense').style('max-width:320px;margin-bottom:0;')
        only_mine = ui.checkbox('Solo i miei', value=True).props('dense')
        btn_refresh = ui.button('Aggiorna', icon='refresh', on_click=lambda: carica_clienti()).props('flat')

    # area risultati
    clienti_list = ui.column().classes('full-width').style('gap:18px;')

    # dati in memoria
    clienti_originali = []   # tutti i clienti (se richiesti)
    miei_clienti_ids = set() # ids dei clienti assegnati al dipendente

    def carica_clienti():
        """Carica i clienti in base al toggle 'only_mine' e aggiorna la cache dei miei clienti."""
        nonlocal clienti_originali, miei_clienti_ids
        # 1) carico la lista 'miei' per poter marcare i clienti anche quando visualizzo tutti
        try:
            resp_miei = api_session.get('/studio/clienti?onlyMine=true')
            if resp_miei.status_code == 200:
                miei = resp_miei.json()
                miei_clienti_ids = {c.get('id') for c in miei if c}
            else:
                miei_clienti_ids = set()
        except Exception:
            miei_clienti_ids = set()

        # 2) carico i clienti da visualizzare: tutti o solo i miei
        try:
            if only_mine.value:
                resp = api_session.get('/studio/clienti?onlyMine=true')
            else:
                resp = api_session.get('/studio/clienti/')
            clienti_originali = resp.json() if resp.status_code == 200 else []
        except Exception as e:
            clienti_originali = []
            print(f"Errore caricamento clienti: {e}")

        # dopo il caricamento, mostra tutti (o filtra se c'è ricerca attiva)
        val = (search.value or '').strip()
        if val and len(val) >= SEARCH_MIN_LENGTH:
            filtra_clienti(val)
        else:
            mostra_tutti_clienti()

    def mostra_tutti_clienti():
        """Mostra tutti i clienti senza filtri (copia dell'originale)."""
        clienti_display = clienti_originali[:]
        render_clienti(clienti_display)

    def filtra_clienti(testo_ricerca):
        """Filtra la lista dei clienti usando tokenizzazione e matching su prefisso.

        - Il filtro viene attivato solo se la lunghezza della stringa >= SEARCH_MIN_LENGTH.
        - I token devono essere prefissi di almeno una parola nei campi controllati (nome, cognome, email).
        """
        testo = testo_ricerca.strip().lower()
        if not testo or len(testo) < SEARCH_MIN_LENGTH:
            mostra_tutti_clienti()
            return

        tokens = [t for t in testo.split() if t]

        def match(cli):
            # Campi utili per la ricerca
            nome = cli.get('utente', {}).get('nome', '')
            cognome = cli.get('utente', {}).get('cognome', '')
            email = cli.get('utente', {}).get('email', '')
            fields = ' '.join([str(nome), str(cognome), str(email)]).lower()
            words = fields.split()
            for token in tokens:
                if not any(w.startswith(token) for w in words):
                    return False
            return True

        clienti_display = [c for c in clienti_originali if match(c)]
        render_clienti(clienti_display)

    def render_clienti(clienti_display):
        """Renderizza la lista clienti dalla lista di display."""
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
                    cliente_id = cli.get('id')

                    # titolo con indicatore "MIO" se assegnato al dipendente
                    is_mio = cliente_id in miei_clienti_ids
                    title = f"{nome} {cognome}"
                    if is_mio:
                        title = f"{title}  •  MIO"

                    ui.label(title).classes('text-body1 q-mb-xs')

                    # opzionale: mostra il dipendente assegnato (se presente nel record cliente)
                    # il backend potrebbe ritornare cliente['responsabile'] = {'nome':..,'cognome':..}
                    resp = cli.get('responsabile')
                    if resp:
                        rnome = resp.get('nome', '')
                        rcognome = resp.get('cognome', '')
                        ui.label(f"Responsabile: {rnome} {rcognome}").classes('text-caption text-grey-6')

                    with ui.row().style('gap:8px;'):
                        ui.button(
                            'Servizi',
                            icon='work',
                            color='primary',
                            on_click=lambda id=cliente_id: visualizza_servizi(id)
                        ).props('flat round')
                        ui.button(
                            'Documenti',
                            icon='folder',
                            color='accent',
                            on_click=lambda id=cliente_id: visualizza_documenti(id)
                        ).props('flat round')

    def visualizza_servizi(cliente_id):
        ui.navigate.to(f'/servizi_cliente/{cliente_id}')

    def visualizza_documenti(cliente_id):
        ui.navigate.to(f'/servizi/{cliente_id}/documenti')

    def on_search_change(e=None):
        val = search.value if search.value is not None else ''
        val = str(val).strip()
        if val == '' or len(val) < SEARCH_MIN_LENGTH:
            mostra_tutti_clienti()
        else:
            filtra_clienti(val)

    # bind eventi
    search.on('update:model-value', on_search_change)
    only_mine.on('click', lambda e=None: carica_clienti())

    # carica iniziale
    carica_clienti()