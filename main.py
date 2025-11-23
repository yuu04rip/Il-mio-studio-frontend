from nicegui import app, ui

import os
app.add_static_files('/static', os.path.join(os.path.dirname(__file__), 'static'))

from app.pages.account.account import account_page
from app.pages.account.account_email import cambia_email_page
from app.pages.account.account_mostra import mostra_dati_account_page
from app.pages.account.account_password import cambia_password_page
from app.pages.auth import login_page, register_page, change_password_page
from app.pages.cliente.documentazione import documentazione_page
from app.pages.home import home_cliente, home_dipendente, home_notaio
from app.pages.dipendente.servizi import servizi_dipendente_page
from app.pages.account.logout import logout_page
from app.pages.cliente.pagamento import pagamento_page
from app.pages.notaio.dipendenti import dipendenti_page
from app.pages.notaio.clienti import clienti_page
from app.pages.notaio.accettazione import accettazione_notaio_page
from app.pages.cliente.servizi_cliente import servizi_cliente_approvati_page
from app.pages.documentazione_servizio_page import documentazione_servizio_page, documentazione_cliente_page
from app.pages.dipendente.servizio_dettagli_page import servizio_dettagli_page
from app.pages.cliente.servizio_cliente_dettagli_page import servizio_cliente_dettagli_page
from app.pages.cliente.documentazione_servizio_cliente_page import documentazione_servizio_page_cliente
from app.pages.dipendente.clienti_dipendente import clienti_page_dipendente
from app.pages.notaio.servizio_dettagli_page_notaio import servizio_dettagli_page_notaio
ui.page('/')(login_page)
ui.page('/register')(register_page)
ui.page('/change_password')(change_password_page)
ui.page('/home_cliente')(home_cliente)
ui.page('/home_dipendente')(home_dipendente)
ui.page('/account/mostra')(mostra_dati_account_page)
ui.page('/account/email')(cambia_email_page)
ui.page('/account/password')(cambia_password_page)
ui.page('/logout')(logout_page)
ui.page('/documentazione')(documentazione_page)
ui.page('/servizi')(servizi_dipendente_page)
ui.page('/pagamento')(pagamento_page)
ui.page('/account')(account_page)
ui.page('/servizi_cliente/{cliente_id}')(servizi_cliente_approvati_page)
ui.page('/dipendenti')(dipendenti_page)
ui.page('/clienti')(clienti_page)
ui.page('/accettazione')(accettazione_notaio_page)
ui.page('/home_notaio')(home_notaio)
ui.page('/servizi/{id}/dettagli')(servizio_dettagli_page)
ui.page('/servizi_cliente/{cliente_id}/dettagli/{servizio_id}')(servizio_cliente_dettagli_page)
ui.page('/documentaizone_servizio_cliente/{servizio_id}')(documentazione_servizio_page_cliente)
ui.page('/clienti_dipendente')(clienti_page_dipendente)
ui.page('/servizi_notaio/{id}/dettagli')(servizio_dettagli_page_notaio)
# --- AGGIUNGI QUESTA ROUTE ---

ui.page('/servizi/{servizio_id}/documenti')(documentazione_servizio_page)
ui.page('/servizi_cliente/{cliente_id}/documenti')(documentazione_cliente_page)
# Serve per l'upload (puoi usare la stessa funzione/pagina)
ui.page('/servizi/{cliente_id}/carica')(documentazione_servizio_page)
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Gestione Studio Notarile", reload=True)