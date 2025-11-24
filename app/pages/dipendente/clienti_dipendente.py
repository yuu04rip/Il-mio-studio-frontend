from nicegui import ui
from app.api.api import api_session

SEARCH_MIN_LENGTH = 2  # soglia minima per attivare il filtro


def clienti_page_dipendente():

    # ------------------------------
    #  CSS PERSONALIZZATO
    # ------------------------------
    ui.html('''
    <style>
.clienti-title {
    background: #1976d2;
    color: white;
    border-radius: 2em;
    padding: 0.6em 2.8em;
    font-weight: 700;
    letter-spacing: 0.05em;
    display: block;
    text-align: center;
    margin: 2em auto 1.5em auto;
    width: fit-content;
    font-size: 2rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

/* Barra di ricerca centrata senza sottolineatura */
.search-bar {
    width: 100%;
    max-width: 600px;
    min-width: 300px;
    margin: 0 auto;
    border-radius: 30px;
    background: rgb(255, 255, 255);
    border: 2px solid rgb(200, 200, 200);
    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
    transition: all 0.18s ease;
    padding: 8px 16px;
}

.search-bar input,
.search-bar .q-field__native {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    background: transparent !important;
    font-size: 1.1rem !important;
    font-weight: 500 !important;
    color: #333 !important;
}

.search-bar input::placeholder {
    font-size: 1.1rem !important;
    color: #888 !important;
}

/* Focus: solo effetto sul bordo esterno, niente underline */
.search-bar:focus-within {
    border-color: rgb(33, 150, 243);
    box-shadow: 0 0 8px rgba(33,150,243,0.18);
}

/* Card principale */
.q-card.main-card {
    background: rgb(240, 240, 240) !important;
    border-radius: 18px !important;
    padding: 10px !important;
    width: 50% !important;
    max-width: 1000px !important;
    margin: 60px auto !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
}

/* Card cliente */
.client-card {
    background:#e3f2fd !important;
    border-radius:0.8em;
    min-height:50px;
    padding:0.5em 1.2em;
    margin-bottom: 0px;
}
    </style>
    ''')

    # ------------------------------
    #  CARD PRINCIPALE
    # ------------------------------
    with ui.row().classes('justify-center').style('width:100%; margin-top:2em;'):
        with ui.card().classes('main-card'):

            # titolo
            ui.label('Clienti').classes('clienti-title').style('margin-bottom:0.5em;')

            # mostra il nome del dipendente
            user = getattr(api_session, 'user', None) or {}
            user_nome = user.get('nome') or user.get('username') or ''
            user_cognome = user.get('cognome') or ''
            if user_nome or user_cognome:
                ui.label(f'Operatore: {user_nome} {user_cognome}') \
                    .classes('text-subtitle2 q-mb-sm') \
                    .style('margin-top:0.2em; margin-bottom:0.5em; text-align:center; width:100%')

            # barra di ricerca + checkbox + bottone
            with ui.row().classes('justify-center q-mb-sm').style('width:100%; text-align:center;'):
                with ui.column().classes('items-center').style('width:100%; max-width:700px;'):
                    search = ui.input(
                        '',
                        placeholder="Cerca per nome o cognome..."
                    ).props('dense borderless').classes('search-bar')

            with ui.row().classes('justify-center').style('width:100%; margin-top:0px; margin-bottom:1em'):
                with ui.row().classes('items-center').style('gap:16px; max-width:400px;'):
                    only_mine = ui.checkbox('Mostra Clienti Personali', value=True).props('dense')
                    btn_refresh = ui.button('Aggiorna', icon='refresh', on_click=lambda: carica_clienti()).props('flat')

            # area risultati
            # area risultati
            with ui.row().classes('justify-center').style('width:100%; margin-top:5px'):
                clienti_list = ui.column().classes('items-center').style('gap:5px; width:100%; max-width:700px;')

            # memoria dati
            clienti_originali = []
            miei_clienti_ids = set()

    # ------------------------------
    #  FUNZIONI LOGICHE
    # ------------------------------
    def carica_clienti():
        nonlocal clienti_originali, miei_clienti_ids

        # lista clienti personali
        try:
            resp_miei = api_session.get('/studio/clienti?onlyMine=true')
            miei_clienti_ids = {c.get('id') for c in resp_miei.json()} if resp_miei.status_code == 200 else set()
        except Exception:
            miei_clienti_ids = set()

        # lista principale
        try:
            if only_mine.value:
                resp = api_session.get('/studio/clienti?onlyMine=true')
            else:
                resp = api_session.get('/studio/clienti/')
            clienti_originali = resp.json() if resp.status_code == 200 else []
        except Exception:
            clienti_originali = []

        # applico eventuale filtro
        val = (search.value or '').strip()
        if val and len(val) >= SEARCH_MIN_LENGTH:
            filtra_clienti(val)
        else:
            mostra_tutti_clienti()

    def mostra_tutti_clienti():
        render_clienti(clienti_originali[:])

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
            return all(any(w.startswith(t) for w in words) for t in tokens)

        clienti_display = [c for c in clienti_originali if match(c)]
        render_clienti(clienti_display)

    def render_clienti(clienti_display):
        clienti_list.clear()
        if not clienti_display:
            with clienti_list:
                ui.label('Nessun cliente trovato.').classes('text-grey-7 q-mt-md')
            return

        for cli in clienti_display:
            with clienti_list:
                with ui.card().classes('client-card'):
                    nome = cli.get('utente', {}).get('nome', '')
                    cognome = cli.get('utente', {}).get('cognome', '')
                    cliente_id = cli.get('id')

                    title = f"{nome} {cognome}"
                    if cliente_id in miei_clienti_ids:
                        title += "  •  MIO"

                    ui.label(title).classes('text-body1 q-mb-xs')

                    resp = cli.get('responsabile')
                    if resp:
                        ui.label(f"Responsabile: {resp.get('nome','')} {resp.get('cognome','')}") \
                            .classes('text-caption text-grey-6')

                    with ui.row().style('gap:8px;'):
                        ui.button(
                            'Servizi',
                            icon='work',
                            color='primary',
                            on_click=lambda id=cliente_id: ui.navigate.to(f'/servizi_cliente/{id}')
                        ).props('flat round')

                        ui.button(
                            'Documenti',
                            icon='folder',
                            color='accent',
                            on_click=lambda id=cliente_id: ui.navigate.to(f'/servizi/{id}/documenti')
                        ).props('flat round')

    # eventi
    search.on('update:model-value', lambda e=None: (
        mostra_tutti_clienti() if not search.value or len(search.value) < SEARCH_MIN_LENGTH
        else filtra_clienti(search.value)
    ))
    only_mine.on('click', lambda e=None: carica_clienti())

    # caricamento iniziale
    carica_clienti()
