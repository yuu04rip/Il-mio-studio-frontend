from nicegui import app, ui

# Serve la cartella static, dovunque essa sia!
import os
app.add_static_files('/static', os.path.join(os.path.dirname(__file__), 'static'))

from app.pages.account.account import account_page
from app.pages.account.account_email import cambia_email_page
from app.pages.account.account_mostra import mostra_dati_account_page
from app.pages.account.account_password import cambia_password_page
from app.pages.auth import login_page, register_page, change_password_page
from app.pages.documentazione import documentazione_page
from app.pages.home import home_cliente, home_dipendente, home_notaio
from app.pages.servizi import servizi_page
from app.pages.account.logout import logout_page
from app.pages.pagamento import pagamento_page
from app.pages.notaio.dipendenti import dipendenti_page
from app.pages.notaio.clienti import clienti_page
from app.pages.notaio.accettazione import accettazione_page

ui.page('/')(login_page)
ui.page('/register')(register_page)
ui.page('/change_password')(change_password_page)
ui.page('/home_cliente')(home_cliente)
ui.page('/home_dipendente')(home_dipendente)
ui.page('/home_notaio')(home_notaio)
ui.page('/account/mostra')(mostra_dati_account_page)
ui.page('/account/email')(cambia_email_page)
ui.page('/account/password')(cambia_password_page)
ui.page('/logout')(logout_page)
ui.page('/documentazione')(documentazione_page)
ui.page('/servizi')(servizi_page)
ui.page('/pagamento')(pagamento_page)
ui.page('/account')(account_page)

# --- NUOVE ROUTE AGGIUNTE QUI ---
ui.page('/dipendenti')(dipendenti_page)
ui.page('/clienti')(clienti_page)
ui.page('/accettazione')(accettazione_page)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Gestione Studio Notarile")