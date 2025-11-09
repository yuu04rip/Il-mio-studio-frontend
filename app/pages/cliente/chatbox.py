from nicegui import ui
from app.api.api import api_session

def chatbox(cliente_id: int):

    ui.add_head_html("""
    <style>
    :root {
        --chat-toggle-size: 50px;
        --chat-toggle-bottom: 125px;
        --chat-toggle-color: #7267EF;
        --chat-panel-width: 400px;
        --chat-panel-height: 420px;
    }

    /* 🌐 Pulsante flottante per aprire la chat */
    .chat-toggle {
        position: fixed;
        bottom: var(--chat-toggle-bottom);
        left: 50%;
        transform: translateX(-50%);
        width: var(--chat-toggle-size);
        height: var(--chat-toggle-size);
        border-radius: 50%;
        background: var(--chat-toggle-color);
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        cursor: pointer;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.25s ease;
    }

    .chat-toggle:hover {
        background: #5b46d1;
    }

    /* 💬 Wrapper chat */
    .chat-wrapper {
        position: fixed;
        left: 50%;
        transform: translateX(-50%);
        bottom: calc(var(--chat-toggle-size) + 20px);
        width: var(--chat-panel-width);
        max-width: calc(100% - 32px);
        background: white;
        border-radius: 16px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.25);
        display: none;
        z-index: 999;
        overflow: hidden;
    }

    .chat-header {
        background: var(--chat-toggle-color);
        color: white;
        padding: 12px 16px;
        font-weight: 600;
        font-size: 1.1em;
    }

    .chat-body {
        height: var(--chat-panel-height);
        display: flex;
        flex-direction: column;
        background: #f8f8f8;
    }

    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 10px;
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .bubble-me {
        background: var(--chat-toggle-color);
        color: white;
        border-radius: 14px;
        padding: 8px 14px;
        align-self: flex-end;
        max-width: 75%;
    }

    .bubble-bot {
        background: white;
        color: var(--chat-toggle-color);
        border-radius: 14px;
        padding: 8px 14px;
        align-self: flex-start;
        max-width: 75%;
    }

    .chat-input-row {
        padding: 10px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        background: white;
        border-top: 1px solid #ddd;
    }

    .chat-input-box {
        width: 100%;
        border-radius: 14px;
        padding: 8px 12px;
        border: 1px solid #ccc;
        box-shadow: inset 0 1px 4px rgba(0,0,0,0.08);
    }

/* 🔘 Pulsanti affiancati */
.chat-buttons-row {
    display: flex;
    justify-content: space-between;
    gap: 80px;
    padding-top: 4px;
}

.chat-btn {
    flex: 1 1 auto !important;
    width: 150px !important;
    height: 32px !important;
    min-height: unset !important;
    border-radius: 10px !important;
    font-size: 0.85em !important;
    font-weight: 600 !important;
    background: var(--chat-toggle-color) !important;
    color: white !important;
    box-shadow: 0 3px 6px rgba(0,0,0,0.2);
    transition: background 0.2s ease;
}

.chat-btn:hover {
    background: #5b46d1 !important;
}

.chat-btn.close {
    background: #999 !important;
}

.chat-btn.close:hover {
    background: #777 !important;
}

    </style>
    """)

    # ---------- LOGICA ----------
    chat_visible = False

    def toggle_chat():
        nonlocal chat_visible
        chat_visible = not chat_visible
        chat_wrapper.style('display: block;' if chat_visible else 'display: none;')
        toggle_button.style('display: none;' if chat_visible else 'display: flex;')

        # 🔹 Trova la card principale e cambia stato visivo
        main_card = ui.query('.q-card')[0] if ui.query('.q-card') else None
        if main_card:
            if chat_visible:
                main_card.remove_class('default')
                main_card.add_class('chat-open')
            else:
                main_card.remove_class('chat-open')
                main_card.add_class('default')

    # 🔘 Pulsante flottante
    with ui.element('button').classes('chat-toggle').on('click', toggle_chat) as toggle_button:
        ui.icon('chat').style('font-size: 1.4rem;')

    # 💬 Contenitore chat
    with ui.element('div').classes('chat-wrapper') as chat_wrapper:
        with ui.row().classes('chat-header'):
            ui.label('Richiesta servizio')
        with ui.element('div').classes('chat-body'):
            chat_container = ui.column().classes('chat-messages').props('id="chat_container"')

            with ui.column().classes('chat-input-row'):
                msg_input = ui.input('', placeholder="Scrivi un messaggio...").classes('chat-input-box')
                # 🔘 Riga dei pulsanti
                with ui.element('div').classes('chat-buttons-row'):

                    def invia_richiesta():
                        testo = msg_input.value.strip()
                        if not testo:
                            ui.notify('Inserisci un messaggio!', color='negative')
                            return

                        with chat_container:
                            ui.label(testo).classes('bubble-me')
                        msg_input.value = ""
                        ui.run_javascript(
                            'document.getElementById("chat_container").scrollTop = document.getElementById("chat_container").scrollHeight;'
                        )

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
                                ui.label('Richiesta ricevuta, ti risponderemo via email!').classes('bubble-bot')
                            ui.notify('Richiesta inviata!', color='positive')
                        else:
                            ui.notify('Errore invio richiesta.', color='negative')

                    # 🔹 Pulsanti affiancati
                    ui.button('Chiudi', on_click=toggle_chat).classes('chat-btn close')
                    ui.button('Invia', on_click=invia_richiesta).classes('chat-btn')
