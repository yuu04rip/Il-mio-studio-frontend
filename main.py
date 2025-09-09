from nicegui import ui

from app.models.notaio import dettaglio_notaio_page
from app.pages.account import account_page
from app.pages.auth import login_page, register_page, change_password_page
from app.pages.documentazione import documentazione_page
from app.pages.home import home_cliente, home_dipendente, home_notaio
from app.models.profile import profile_page, edit_profile_page
from app.models.dipendente_tecnico import add_dipendente_page
from app.models.cliente import clienti_lista_page, dettaglio_cliente_page
from app.models.servizio import servizi_cliente_page
from app.models.documentazione import documentazione_cliente_page
from app.models.accettazione import accettazione_servizi_page
from app.pages.servizi import servizi_page

ui.page('/')(login_page)
ui.page('/register')(register_page)
ui.page('/change_password')(change_password_page)
ui.page('/home_cliente')(home_cliente)
ui.page('/home_dipendente')(home_dipendente)
ui.page('/home_notaio')(home_notaio)
ui.page('/profilo')(profile_page)
ui.page('/profilo/edit')(edit_profile_page)
ui.page('/dipendenti/aggiungi')(add_dipendente_page)
ui.page('/documentazione')(documentazione_cliente_page)
ui.page('/servizi')(servizi_cliente_page)
ui.page('/clienti')(clienti_lista_page)
ui.page('/clienti/{cliente_id}')(dettaglio_cliente_page)
ui.page('/accettazione')(accettazione_servizi_page)
ui.page('/notaio')(dettaglio_notaio_page)
ui.page('/account')(account_page)
ui.page('/documentazione')(documentazione_page)
ui.page('/servizi')(servizi_page)
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Gestione Studio Notarile")