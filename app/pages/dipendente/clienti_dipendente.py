from nicegui import ui
from app.api.api import api_session

SEARCH_MIN_LENGTH = 2  # soglia minima per attivare il filtro


def clienti_page_dipendente():

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
    font-size: 2rem; /* ⬅️ aumenta qui (1.8–2.4rem sono valori ideali) */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}
/* 🔹 Barra di ricerca centrata perfettamente sotto al titolo */
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


/* 🔹 Centra anche la row che contiene la barra */
.q-row {
    justify-content: center !important;
}


.search-bar input,
.search-bar .q-field__native {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    background: transparent !important;
}

.search-bar .q-field__control,
.search-bar .q-field__control::before,
.search-bar .q-field__control::after {
    border: none !important;
    box-shadow: none !important;
}

.search-bar:focus-within {
    border-color: rgb(33, 150, 243);
    box-shadow: 0 0 8px rgba(33,150,243,0.18);
}
/* 🔹 Testo interno della barra di ricerca più grande */
.search-bar input,
.search-bar .q-field__native {
    font-size: 1.1rem !important;   /* aumenta o diminuisci a piacere (es. 1.2rem) */
    font-weight: 500 !important;
    color: #333 !important;         /* testo più leggibile */
}

/* 🔹 Placeholder (testo grigio quando vuoto) */
.search-bar input::placeholder {
    font-size: 1.1rem !important;
    color: #888 !important;
}
/* 🧱 CARD PRINCIPALE (contenitore centrale) */
.q-card {
background: rgb(240, 240, 240) !important;
border-radius: 18px !important;
box-shadow: 0 8px 24px rgba(0, 0, 0) !important;
padding: 10px !important;                  /* spazio interno più grande */

/* 🔹 CONTROLLO DIMENSIONI */
width: 50% !important; 
max-height: 500px !important;                    /* card più larga (percentuale dello schermo) */
max-width: 1000px !important;              /* larghezza massima (per non esagerare su monitor grandi) */

/* 🔹 CENTRATURA VISIVA */
margin: 60px auto !important;              /* centrata orizzontalmente e con margine sopra/sotto */

/* 🔹 Centro totale nella finestra */
display: flex !important;
flex-direction: column !important;
justify-content: center !important; /* centra verticalmente */
align-items: center !important;     /* centra orizzontalmente */
}

            /* 🧱 CARD CLIENTI */
.client-card.q-card {
    background:#e3f2fd !important;
    border-radius:0.8em;
    min-height:50px;        /* card più bassa */
    padding:0.5em 1.2em;    /* padding ridotto */
    margin-bottom: 0px;     /* margine tra card */
}

    </style>
    ''')
    with ui.row().classes('justify-center').style('width:100%; margin-top:2em;'):
        with ui.card().classes('q-card'):
                ui.label('Clienti').classes('clienti-title').style('margin-bottom:0.5em;')


                # mostra il nome del dipendente (se disponibile in api_session.user)
                user = getattr(api_session, 'user', None) or {}
                user_nome = user.get('nome') or user.get('username') or ''
                user_cognome = user.get('cognome') or ''
                if user_nome or user_cognome:
                    ui.label(f'Operatore: {user_nome} {user_cognome}').classes('text-subtitle2 q-mb-sm').style('margin-top:0.2em; margin-bottom:0.5em; text-align:center; width:100%')

                # barra di ricerca + checkbox "solo i miei"
                # 🔹 Barra di ricerca centrata sotto il titolo
            # 🔹 Prima riga: solo la barra di ricerca
                with ui.row().classes('justify-center q-mb-sm').style('width:100%; text-align:center;'):
                    with ui.column().classes('items-center').style('width:100%; max-width:700px;'):
                        search = ui.input('', placeholder="Cerca per nome o cognome...") \
                            .props('dense outlined') \
                            .classes('search-bar')
                # 🔹 Seconda riga: checkbox + bottone
                with ui.row().classes('justify-center').style('width:100%; margin-top:0px;'):
                    with ui.row().classes('items-center').style('gap:16px; max-width:400px; display:flex;'):
                        only_mine = ui.checkbox('Mostra Clienti Personali', value=True).props('dense')
                        btn_refresh = ui.button('Aggiorna', icon='refresh', on_click=lambda: carica_clienti()).props('flat')

                # area risultati
                with ui.row().classes('justify-center').style('width:100%; margin-top: -40px'):
                    clienti_list = ui.column().classes('items-center').style('gap:5px; width:100%; max-width:700px;')

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
                with ui.card().classes('client-card'):
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