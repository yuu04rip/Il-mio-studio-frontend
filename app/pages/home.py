from nicegui import ui
from app.pages.cliente.chatbox import chatbox

def home_cliente(cliente_id: int):
    ui.add_head_html("""
    <style>
/* 🌄 SFONDO GENERALE DELLA PAGINA */
body {
    background: linear-gradient(

        rgb(255, 255, 255) 100%   /* bianco puro */
    );
    font-family: 'Poppins', sans-serif; /* font moderno e pulito */
}

/* 🧱 CARD PRINCIPALE (contenitore centrale) */
.q-card {
    background: rgb(240, 240, 240) !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0) !important;
    padding: 48px !important;                  /* spazio interno più grande */

    /* 🔹 CONTROLLO DIMENSIONI */
    width: 80% !important;                     /* card più larga (percentuale dello schermo) */
    max-width: 1000px !important;              /* larghezza massima (per non esagerare su monitor grandi) */
    min-height: 600px !important;              /* altezza minima maggiore */

    /* 🔹 CENTRATURA VISIVA */
    margin: 60px auto !important;              /* centrata orizzontalmente e con margine sopra/sotto */

    /* 🔹 Centro totale nella finestra */
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important; /* centra verticalmente */
    align-items: center !important;     /* centra orizzontalmente */
}

/* 🏷 LABEL "HOME" (titolo principale) */
.text-h5 {
    /* 🔹 Testo e colore */
    font-size: 1.8rem !important;             /* leggermente più grande */
    font-weight: 700 !important;              /* grassetto */
    letter-spacing: 0.06em;                   /* spaziatura più elegante */
    color: rgb(255, 255, 255);                /* bianco puro */
    background: rgb(35, 150, 245);            /* blu acceso (#2196f3) */

    /* 🔹 Dimensioni e forma */
    border-radius: 40px;                      /* forma più arrotondata */
    padding: 16px 80px;                       /* più spazio interno (verticale/orizzontale) */
    width: 60%;                               /* più largo, 60% della card */
    max-width: 600px;                         /* limite massimo di larghezza */
    margin: -100px auto 75px auto;                 /* centrato orizzontalmente + spazio sotto */
    display: block;                           /* blocco centrabile */
    text-align: center;                       /* testo centrato all’interno */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); /* ombra leggera per rilievo */
}

/* 🎛 CONTENITORE DELLE RIGHE DEI BOTTONI */
.q-row {
    justify-content: center !important; /* centra orizzontalmente i bottoni */
    align-items: center !important;     /* centra verticalmente nella riga */
    gap: 32px;                          /* distanza costante tra i bottoni */
    margin-top: 24px;                   /* spazio sopra la prima riga */
}

/* 🔘 BOTTONI UNIFORMI */
.q-btn {
    background-color: rgb(25, 120, 210) !important; /* blu principale */
    color: rgb(255, 255, 255) !important;           /* testo bianco */
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    border-radius: 50px !important;
    transition: all 0.3s ease;

    /* 🔹 Dimensioni uniformi */
    width: 400px !important;   /* larghezza fissa */
    height: 100px !important;  /* altezza fissa */

    /* 🔹 Allineamento interno (icona + testo) */
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 12px !important;      /* distanza tra icona e testo */
}

/* ✨ EFFETTO HOVER SUI BOTTONI */
.q-btn:hover {
    background-color: rgb(13, 71, 161) !important;  /* blu più scuro */
    transform: translateY(-4px);                    /* leggero sollevamento */
}
</style>

    """)





    from app.pages.cliente.chatbox import chatbox


def home_cliente(cliente_id: int):
    ui.add_head_html('<link rel="stylesheet" href="/static/stylesHome.css">')

    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        ui.label('HOME').classes('text-h5 q-mb-lg').style(
            'background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;'
        )
        with ui.row().classes('q-gutter-lg q-mb-md'):
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')).classes('q-pa-xl').style('min-width:160px;')
            ui.button('DOCUMENTAZIONE', icon='folder', on_click=lambda: ui.navigate.to('/documentazione')).classes('q-pa-xl').style('min-width:160px;')
        with ui.row().classes('q-gutter-lg'):
            ui.button('EFFETTUA PAGAMENTO', icon='payments', on_click=lambda: ui.navigate.to('/pagamento')).classes('q-pa-xl').style('min-width:160px;')
            ui.button('SERVIZI', icon='work',
                      on_click=lambda: ui.navigate.to(f'/servizi_cliente/{cliente_id}')
                      ).classes('q-pa-xl').style('min-width:160px;')

    chatbox(cliente_id)

def home_dipendente():
    ui.add_head_html('<link rel="stylesheet" href="/static/stylesHome.css">')
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto'):
        ui.label('HOME').classes('text-h5 q-mb-lg') \
            .style('background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;')
        with ui.row().classes('q-gutter-lg q-mb-md'):
            ui.button('CLIENTI', icon='groups', on_click=lambda: ui.navigate.to('/clienti_dipendente')) \
                .classes('q-pa-xl').style('min-width:160px;')
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')) \
                .classes('q-pa-xl').style('min-width:160px;')
        with ui.row().classes('q-gutter-lg'):
            ui.button('SERVIZI ARCHIVIATI', icon='work', on_click=lambda: ui.navigate.to('/servizi')) \
                .classes('q-pa-xl').style('min-width:160px;')

def home_notaio():
    ui.add_head_html('<link rel="stylesheet" href="/static/stylesHome.css">')
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto shadow-5') \
            .style('max-width:550px;background:#fafdff;'):
        ui.label('HOME').classes('text-h5 q-mb-lg').style(
            'background:#2196f3;color:white;border-radius:2em;padding:.5em 3em;display:block;text-align:center;letter-spacing:0.04em;font-weight:700;font-size:1.32em;margin-bottom:28px;'
        )
        with ui.row().classes('q-gutter-lg q-mb-md').style('justify-content:center;'):
            ui.button('CLIENTI', icon='groups', on_click=lambda: ui.navigate.to('/clienti')) \
                .classes('q-pa-xl').style('min-width:160px;font-weight:600;font-size:1.08em;')
            ui.button('ACCOUNT', icon='person', on_click=lambda: ui.navigate.to('/account')) \
                .classes('q-pa-xl').style('min-width:160px;font-weight:600;font-size:1.08em;')
        with ui.row().classes('q-gutter-lg').style('justify-content:center;'):
            ui.button('DIPENDENTI', icon='add', on_click=lambda: ui.navigate.to('/dipendenti')) \
                .classes('q-pa-xl').style('min-width:160px;font-weight:600;font-size:1.08em;')
            ui.button('ACCETTAZIONE', icon='check', on_click=lambda: ui.navigate.to('/accettazione')) \
                .classes('q-pa-xl').style('min-width:160px;font-weight:600;font-size:1.08em;')
            ui.button('ARCHIVIAZIONE', icon='folder', on_click=lambda: ui.navigate.to('/servizi_notaio_archiviati')) \
                .classes('q-pa-xl').style('min-width:160px;font-weight:600;font-size:1.08em;')