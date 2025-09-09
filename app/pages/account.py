from nicegui import ui

def account_page():
    # Sfondo chiaro (opzionale: puoi metterlo anche fuori dalla card se vuoi tutto bianco)
    with ui.column().classes('items-center q-mt-xl'):
        with ui.card().classes('glass-card shadow-7').style('max-width:440px;min-width:340px;padding:54px 0 44px 0;'):
            # Titolo elegante
            ui.label('Area personale').classes('text-h5 glass-title').style(
                'font-weight:700;font-size:2em;letter-spacing:0.04em;margin-bottom:1.7em;'
            )
            # Bottoni azione con icone Material
            actions = [
                ('account_circle', 'Mostra dati account', '/account/mostra'),
                ('edit',           'Modifica dati anagrafici', '/account/modifica'),
                ('mail',           'Cambia email', '/account/email'),
                ('vpn_key',        'Modifica password', '/account/password'),
            ]
            for icon, label, path in actions:
                with ui.button(on_click=lambda p=path: ui.navigate.to(p)).classes('glass-btn full-width'):
                    ui.icon(icon).classes('glass-icon')
                    ui.label(label).classes('glass-btn-label')

    ui.add_head_html("""
    <style>
    body { background: linear-gradient(115deg, #e3f0fc 0%, #f7faff 90%); }
    .glass-card {
        background: rgba(242, 247, 252, 0.72) !important;
        box-shadow: 0 8px 32px 0 #1976d211, 0 1.5px 7px 0 #00000006 !important;
        border-radius: 2em !important;
        border: 1.2px solid rgba(190,210,235,0.22) !important;
        backdrop-filter: blur(7px);
        -webkit-backdrop-filter: blur(7px);
        min-height: 430px;
    }
    .glass-title {
        background: linear-gradient(90deg, #2196f3 60%, #42a5f5 100%);
        color: #fff !important;
        border-radius:2em;
        padding:.6em 1.6em .6em 1.6em;
        box-shadow: 0 2px 14px 0 #2196f341;
        margin: 0 auto 38px auto;
        text-align: center;
        display: block;
        width: fit-content;
    }
    .glass-btn {
        background: rgba(255,255,255,0.70) !important;
        border-radius: 1.3em !important;
        margin: 0.6em 0;
        padding: 0.8em 0 0.8em 0 !important;
        min-height: 3.1em;
        font-size: 1.15em;
        box-shadow: 0 2px 12px 0 #1976d21a;
        color: #1867c0 !important;
        display: flex;
        align-items: center;
        transition: background .18s, color .18s, box-shadow .22s, transform .14s;
    }
    .glass-btn:hover, .glass-btn:focus {
        background: #2196f3 !important;
        color: #fff !important;
        box-shadow: 0 2px 22px 0 #2196f349 !important;
        transform: scale(1.038);
    }
    .glass-btn-label {
        font-weight: 500;
        letter-spacing: 0.03em;
        margin-left: .7em;
        font-size:1.12em;
        color: inherit !important;
        transition: color .18s;
    }
    .glass-btn:hover .glass-btn-label,
    .glass-btn:focus .glass-btn-label {
        color: #fff !important;
    }
    .glass-icon {
        font-size: 1.45em !important;
        color: #2196f3 !important;
        transition: color .18s;
    }
    .glass-btn:hover .glass-icon,
    .glass-btn:focus .glass-icon {
        color: #fff !important;
    }
    </style>
    """)
