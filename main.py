from nicegui import ui


from app.pages.account import account_page
from app.pages.account_email import cambia_email_page
from app.pages.account_mostra import mostra_dati_account_page
from app.pages.account_password import cambia_password_page
from app.pages.auth import login_page, register_page, change_password_page
from app.pages.documentazione import documentazione_page
from app.pages.home import home_cliente, home_dipendente, home_notaio
from app.pages.servizi import servizi_page
from app.pages.logout import logout_page

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


ui.page('/account')(account_page)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Gestione Studio Notarile")