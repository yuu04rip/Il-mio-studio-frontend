import requests

BACKEND_URL = 'http://localhost:8000'  # Cambia con il tuo backend

class APISession:
    def __init__(self):
        self.token = None
        self.user = None

    def set_token(self, token: str):
        self.token = token

    def set_user(self, user: dict):
        self.user = user

    def _headers(self):
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}

    def post(self, url, data=None, **kwargs):   # <--- AGGIUNGI **kwargs
        full_url = f'http://localhost:8000{url}' if url.startswith('/') else url
        # Passa sia data che json (o altro) a requests.post!
        return requests.post(full_url, data=data, headers=self._headers(), **kwargs)

    def get(self, endpoint: str):
        return requests.get(f"{BACKEND_URL}{endpoint}", headers=self._headers())

    def put(self, endpoint: str, data: dict):
        return requests.put(f"{BACKEND_URL}{endpoint}", json=data, headers=self._headers())

    def delete(self, endpoint: str):
        return requests.delete(f"{BACKEND_URL}{endpoint}", headers=self._headers())
    def register_dipendente(self, user_data):
        """Registra un dipendente tramite endpoint dedicato."""
        resp = requests.post(f"{BACKEND_URL}/auth/register-dipendente", json=user_data)
        resp.raise_for_status()
        data = resp.json()
        self.token = data.get("access_token")
        return data
    def search_clienti(self, query):
        """Cerca clienti per nome o cognome (substring, case-insensitive)."""
        resp = requests.get(f"{BACKEND_URL}/studio/clienti/search/", params={"q": query}, headers=self._headers())
        resp.raise_for_status()
        return resp.json()
    def invia_chat_richiesta_servizio(self, cliente_id: int, testo: str):
        """Invia una richiesta servizio via mini chat/email."""
        resp = requests.post(
        f"{BACKEND_URL}/studio/servizi/richiesta-chat",
        json={"cliente_id": cliente_id, "testo": testo},
        headers=self._headers()
    )
        resp.raise_for_status()
        return resp.json()
api_session = APISession()