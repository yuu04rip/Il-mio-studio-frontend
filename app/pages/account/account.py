from nicegui import ui

def account_page():
    ui.query('body').style(
        'display:flex;justify-content:center;align-items:center;height:100vh;margin:0;'
    )

    with ui.column().classes('items-center q-mt-xl'):
        # --- Main Card ---
        with ui.card().classes('glass-card shadow-7').style(
            'background:#f0f0f0;max-width:440px;min-width:340px;padding:54px 0 44px 0;'
            'display:flex;flex-direction:column;align-items:center;justify-content:center; border-radius:2.5em;'
        ):
            # --- Title ---
            ui.label('Area personale').classes('glass-title').style(
                'color:#1976d2;text-align:center;font-size:3em;font-weight:bold;margin-bottom:20px;'
            )

            # --- Button actions ---
            actions = [
                ('account_circle', 'Mostra dati account', '/account/mostra'),
                ('mail', 'Cambia email', '/account/email'),
                ('vpn_key', 'Modifica password', '/account/password'),
                ('logout', 'Logout', '/logout'),
            ]

            for icon, label, path in actions:
                with ui.button(on_click=lambda p=path: ui.navigate.to(p)).classes(
                    'glass-btn'
                ).style(
                    'background: linear-gradient(90deg, #2196f3 70%, #1976d2 100%) !important;color:#fff !important;position:relative;display:flex;align-items:center;justify-content:center;'
                    'max-width:330px;min-width:280px;'
                    'margin-top:12px;border-radius:12px;border-radius:1.8em;'
                ):
                    # Icon positioned on the left
                    ui.icon(icon).classes('glass-icon').style(
                        'position:absolute;left:10px; color:white;font-size:2em;'
                    )
                    # Centered label
                    ui.label(label).classes('glass-btn-label').style(
                        'text-align:center;font-size:1.2em;color:white;margin:7.5px;'
                    )
