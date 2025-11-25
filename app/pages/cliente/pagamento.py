from nicegui import ui

def pagamento_page():
    with ui.card().classes('q-pa-xl q-mt-xl q-mx-auto').style('max-width:800px;'):
        ui.label("Volevi i miei soldi, NEGRO DI MERDA 😁").classes("text-h4 q-mb-md").style("color:#d32f2f;")
        # Video grande e autoplay
        ui.html("""
            <video width="100%" height="480" controls autoplay loop style="border-radius:1.5em;box-shadow:0 4px 24px #0002;">
                <source src="/static/rickroll.mp4" type="video/mp4">
                Il tuo browser non supporta il video tag.
            </video>
            """, sanitize=False)