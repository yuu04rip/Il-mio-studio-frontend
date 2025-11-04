from nicegui import ui

def header(title="Il Mio Studio"):
    with ui.row().classes("q-pa-md bg-primary text-white"):
        ui.avatar(icon='person', size='lg')
        ui.label(title).classes("text-h5 q-ml-md")

def big_button(text, icon=None, on_click=None):
    return ui.button(text, icon=icon, on_click=on_click).props('rounded unelevated size="xl" color="secondary"').classes('q-mb-md q-mr-md q-pa-lg text-h6')