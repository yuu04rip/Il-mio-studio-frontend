from app.api.api_client import APIClient

class GestoreLogin:
    def __init__(self, api: APIClient):
        self.api = api
        self.utente_corrente = None

    def aggiungi_utente(self, user_data: dict):
        # user_data: dict con chiavi come RegisterRequest
        res = self.api.register(user_data)
        # Dopo la registrazione, aggiorna utente_corrente
        self.utente_corrente = self.api.get_me()
        return self.utente_corrente

    def login(self, email: str, password: str):
        res = self.api.login(email, password)
        # Dopo il login, aggiorna utente_corrente
        self.utente_corrente = self.api.get_me()
        return self.utente_corrente

    def recupera_credenziali(self, email: str, codice: int):
        # Endpoint non presente nel backend, puoi implementare qui una possibile azione futura
        raise NotImplementedError("Endpoint di recupero credenziali non implementato nel backend.")