from app.api.api_client import APIClient

class GestoreStudio:
    def __init__(self, api: APIClient):
        self.api = api

    # --- Gestione Dipendenti/Notai ---
    def aggiungi_dipendente(self, user_data: dict, tipo: str):
        # tipo: "contabile", "notaio", "assistente" (TipoDipendenteTecnico)
        return self.api.add_dipendente(user_data, tipo)

    def aggiungi_notaio(self, user_data: dict, codice_notarile: int):
        return self.api.add_notaio(user_data, codice_notarile)

    # --- Gestione Documentazione ---
    def carica_documentazione(self, cliente_id: int, tipo: str, filepath: str):
        return self.api.carica_documentazione(cliente_id, tipo, filepath)

    def visualizza_documentazione(self, cliente_id: int):
        return self.api.visualizza_documentazione(cliente_id)

    def sostituisci_documentazione(self, doc_id: int, filepath: str):
        return self.api.sostituisci_documentazione(doc_id, filepath)

    # --- Gestione Servizi ---
    def archivia_servizio(self, servizio_id: int):
        return self.api.archivia_servizio(servizio_id)

    def inizializza_servizio(self, cliente_nome: str, tipo: str, codiceCorrente: int, codiceServizio: int):
        # tipo: "atto", "compromesso", "preventivo" (TipoServizio)
        return self.api.inizializza_servizio(cliente_nome, tipo, codiceCorrente, codiceServizio)