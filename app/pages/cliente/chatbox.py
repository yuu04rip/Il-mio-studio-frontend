from nicegui import ui
from app.api.api import api_session

def chatbox(cliente_id: int):
    # Stato visibilità chat
    chat_visible = False

    def toggle_chat():
        nonlocal chat_visible
        chat_visible = not chat_visible
        if chat_visible:
            chat_wrapper.style('display: block;')
            toggle_button.style('display: none;')
        else:
            chat_wrapper.style('display: none;')
            toggle_button.style('display: block;')

    # Bottone flottante
    with ui.element('div').classes('fixed') as toggle_button:
        ui.button(icon='chat', on_click=toggle_chat) \
            .classes('bg-purple-600 text-white') \
            .style('border-radius:50%;width:56px;height:56px;box-shadow:0 2px 8px #7267ef44;z-index:1000;margin:2em;bottom:0;right:0;position:fixed;')

    # Contenitore chat
    with ui.element('div').classes('fixed-bottom') as chat_wrapper:
        chat_wrapper.style('max-width:390px;margin:auto;left:0;right:0;z-index:999;display:none;')

        # Titolo
        with ui.row().classes('q-pa-md').style('background: #7267EF; border-radius: 1.2em 1.2em 0 0; align-items:center;'):
            ui.label('Richiesta servizio').style('color:white;font-size:1.25em;font-weight:600;flex:1;')
            ui.icon('close').style('color:white;cursor:pointer;').on('click', toggle_chat)

        # Corpo chat
        with ui.element('div').classes('chatbot-body').style(
                'display: flex; flex-direction: column; height: 300px; '
                'background-color: #f9f9f9; '
                'background-image: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'52\' height=\'52\' viewBox=\'0 0 52 52\'%3E%3Cpath fill=\'%23aca992\' fill-opacity=\'0.4\' d=\'M0 17.83V0h17.83a3 3 0 0 1-5.66 2H5.9A5 5 0 0 1 2 5.9v6.27a3 3 0 0 1-2 5.66zm0 18.34a3 3 0 0 1 2 5.66v6.27A5 5 0 0 1 5.9 52h6.27a3 3 0 0 1 5.66 0H0V36.17zM36.17 52a3 3 0 0 1 5.66 0h6.27a5 5 0 0 1 3.9-3.9v-6.27a3 3 0 0 1 0-5.66V52H36.17zM0 31.93v-9.78a5 5 0 0 1 3.8.72l4.43-4.43a3 3 0 1 1 1.42 1.41L5.2 24.28a5 5 0 0 1 0 5.52l4.44 4.43a3 3 0 1 1-1.42 1.42L3.8 31.2a5 5 0 0 1-3.8.72zm52-14.1a3 3 0 0 1 0-5.66V5.9A5 5 0 0 1 48.1 2h-6.27a3 3 0 0 1-5.66-2H52v17.83zm0 14.1a4.97 4.97 0 0 1-1.72-.72l-4.43 4.44a3 3 0 1 1-1.41-1.42l4.43-4.43a5 5 0 0 1 0-5.52l-4.43-4.43a3 3 0 1 1 1.41-1.41l4.43 4.43c.53-.35 1.12-.6 1.72-.72v9.78zM22.15 0h9.78a5 5 0 0 1-.72 3.8l4.44 4.43a3 3 0 1 1-1.42 1.42L29.8 5.2a5 5 0 0 1-5.52 0l-4.43 4.44a3 3 0 1 1-1.41-1.42l4.43-4.43a5 5 0 0 1-.72-3.8zm0 52c.13-.6.37-1.19.72-1.72l-4.43-4.43a3 3 0 1 1 1.41-1.41l4.43 4.43a5 5 0 0 1 5.52 0l4.43-4.43a3 3 0 1 1 1.42 1.41l-4.44 4.43c.36.53.6 1.12.72 1.72h-9.78zm9.75-24a5 5 0 0 1-3.9 3.9v6.27a3 3 0 1 1-2 0V31.9a5 5 0 0 1-3.9-3.9h-6.27a3 3 0 1 1 0-2h6.27a5 5 0 0 1 3.9-3.9v-6.27a3 3 0 1 1 2 0v6.27a5 5 0 0 1 3.9 3.9h6.27a3 3 0 1 1 0 2H31.9z\'%3E%3C/path%3E%3C/svg%3E"); '
                'border-radius: 0 0 1.2em 1.2em; overflow: hidden;'
        ):
            chat_container = ui.column().classes('chat-messages').props('id="chat_container"') \
                .style('flex: 1; overflow-y: auto; gap: 4px; padding: 8px;')

            # Input
            with ui.row().classes('chat-input-row').style('gap:4px;padding:8px;border-top:1px solid #ccc;'):
                msg_input = ui.input('', placeholder="Scrivi un messaggio...").classes('chat-input-box') \
                    .style('flex:1;border-radius:2em;background:white;box-shadow:0 1px 6px #7267ef22;font-size:1em;')

                def invia_richiesta():
                    testo = msg_input.value.strip()
                    if not testo:
                        ui.notify('Inserisci un messaggio!', color='negative')
                        return

                    # Bubble utente
                    with chat_container:
                        ui.label(testo).classes('bubble-me') \
                            .style('background:#7267EF;color:white;border-radius:1.2em;max-width:75%;padding:.7em 1.4em;align-self:flex-end;margin-bottom: 4px;')

                    msg_input.value = ""

                    # Scroll automatico
                    ui.run_javascript('document.getElementById("chat_container").scrollTop = document.getElementById("chat_container").scrollHeight;')

                    try:
                        resp = api_session.post(
                            '/studio/servizi/richiesta-chat',
                            json={'cliente_id': cliente_id, 'testo': testo}
                        )
                    except Exception:
                        ui.notify('Connessione fallita.', color='negative')
                        return

                    if resp.status_code == 200:
                        with chat_container:
                            ui.label('Richiesta ricevuta, ti risponderemo via email!').classes('bubble-bot') \
                                .style('background:white;color:#7267EF;border-radius:1.2em;max-width:75%;padding:.7em 1.4em;align-self:flex-start;margin-bottom: 4px;')

                        ui.run_javascript('document.getElementById("chat_container").scrollTop = document.getElementById("chat_container").scrollHeight;')
                        ui.notify('Richiesta inviata!', color='positive')
                    else:
                        ui.notify('Errore invio richiesta.', color='negative')

                ui.button(icon='send', on_click=invia_richiesta).style('color:#7267EF;font-size:1.35em;margin-right:.4em;')

    # Stili CSS
    ui.add_head_html("""
<style>
.chat-messages {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    min-height: 0;
}
.bubble-me {
    background: #7267EF;
    color: white;
    border-radius: 1.2em;
    max-width: 75%;
    padding: .7em 1.4em;
    align-self: flex-end;
    margin-bottom: 4px;
}
.bubble-bot {
    background: white;
    color: #7267EF;
    border-radius: 1.2em;
    max-width: 75%;
    padding: .7em 1.4em;
    align-self: flex-start;
    margin-bottom: 4px;
}
</style>
""")
