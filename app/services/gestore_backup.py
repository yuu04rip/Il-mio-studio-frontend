from app.api.api_client import APIClient

class GestoreBackup:
    def __init__(self, api: APIClient):
        self.api = api

    def archivia_servizio(self, servizio_id: int):
        return self.api.archivia_servizio(servizio_id)

    def mostra_servizi_archiviati(self):
        # Endpoint non presente, da implementare lato backend e in APIClient
        raise NotImplementedError("Endpoint mostra_servizi_archiviati non implementato")

    def modifica_servizio_archiviato(self, servizio_id: int, nuovi_dati: dict):
        # Endpoint non presente, da implementare lato backend e in APIClient
        raise NotImplementedError("Endpoint modifica_servizio_archiviato non implementato")