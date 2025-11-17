from nicegui import ui
from app.api.api import api_session

SEARCH_MIN_LENGTH = 2  # soglia minima per attivare il filtro

def clienti_page():
    # variabili
    search = None
    clienti_list = None
    clienti_originali = []   
    miei_clienti_ids = set() 

    # === STILI GRAFICI ===
    ui.html('''
    <style>
    /* 🌄 SFONDO GENERALE */
    body {
        background: linear-gradient(rgb(255, 255, 255) 100%);
        font-family: 'Poppins', sans-serif;
    }

    /* 🧱 CARD PRINCIPALE (contenitore centrale) */
    .main-card.q-card {
        background: rgb(240, 240, 240) !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0) !important;
        padding: 10px !important;

        /* 🔹 DIMENSIONI */
        width: 50% !important;
        max-width: 1000px !important;
        max-height: 500px !important;

        /* 🔹 CENTRATURA */
        margin: 60px auto !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* 🏷️ TITOLO "CLIENTI" */
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

    /* 🔹 BARRA DI RICERCA */
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

    .search-bar:focus-within {
        border-color: rgb(33, 150, 243);
        box-shadow: 0 0 8px rgba(33,150,243,0.18);
    }

    .search-bar input::placeholder {
        font-size: 1.1rem !important;
        color: #888 !important;
    }

    /* 🧱 CARD CLIENTI */
    .client-card.q-card {
        background:#e3f2fd !important;
        border-radius:0.8em !important;
        min-height:50px;
        padding:0.5em 1.2em;
        margin-bottom: 8px;
    }

    /* 🔹 BOTTONI ALL’INTERNO DELLE CARD */
    .client-card .q-btn {
        border-radius:50px !important;
    }
    </style>
    ''')

    # === STRUTTURA DELLA PAGINA ===
    with ui.row().classes('justify-center').style('width:100%; margin-top:2em;'):
        with ui.card().classes('main-card'):
            with ui.column().classes('items-center').style('gap:20px; width:100%;'):

                # Titolo
                ui.label('Clienti').classes('clienti-title')

                # Barra di ricerca
                search = ui.input('', placeholder="Cerca per nome o cognome...") \
                    .props('dense borderless') \
                    .classes('search-bar').style('margin-bottom: 40px;')

                # Area risultati
                clienti_list = ui.column().classes('items-center').style('gap:8px; width:100%; max-width:700px;')

    # === FUNZIONI ===

    def carica_clienti():
        """Carica i clienti e aggiorna la lista."""
        nonlocal clienti_originali, miei_clienti_ids
        try:
            resp_miei = api_session.get('/studio/clienti?onlyMine=true')
            miei_clienti_ids = {c.get('id') for c in resp_miei.json()} if resp_miei.status_code == 200 else set()
        except Exception:
            miei_clienti_ids = set()

        try:
            resp = api_session.get('/studio/clienti/')
            clienti_originali = resp.json() if resp.status_code == 200 else []
        except Exception as e:
            clienti_originali = []
            print(f"Errore caricamento clienti: {e}")

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
            words = (f"{nome} {cognome} {email}".lower()).split()
            return all(any(w.startswith(token) for w in words) for token in tokens)

        render_clienti([c for c in clienti_originali if match(c)])

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
                    is_mio = cliente_id in miei_clienti_ids
                    title = f"{nome} {cognome}" + ("  •  MIO" if is_mio else "")
                    ui.label(title).classes('text-body1 q-mb-xs')
                    resp = cli.get('responsabile')
                    if resp:
                        ui.label(f"Responsabile: {resp.get('nome', '')} {resp.get('cognome', '')}").classes('text-caption text-grey-6')
                    with ui.row().style('gap:8px;'):
                        ui.button('Servizi', icon='work', color='primary',
                                  on_click=lambda id=cliente_id: visualizza_servizi(id)).props('flat round')
                        ui.button('Documenti', icon='folder', color='accent',
                                  on_click=lambda id=cliente_id: visualizza_documenti(id)).props('flat round')

    def visualizza_servizi(cliente_id):
        ui.navigate.to('/accettazione')

    def visualizza_documenti(cliente_id):
        ui.navigate.to(f'/documentazione_cliente/{cliente_id}')

    def on_search_change(e=None):
        val = (search.value or '').strip()
        if val == '' or len(val) < SEARCH_MIN_LENGTH:
            mostra_tutti_clienti()
        else:
            filtra_clienti(val)

    search.on('update:model-value', on_search_change)
    carica_clienti()
