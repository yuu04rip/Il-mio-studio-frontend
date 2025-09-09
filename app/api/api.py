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

    def post(self, endpoint: str, data: dict):
        return requests.post(f"{BACKEND_URL}{endpoint}", json=data, headers=self._headers())

    def get(self, endpoint: str):
        return requests.get(f"{BACKEND_URL}{endpoint}", headers=self._headers())

    def put(self, endpoint: str, data: dict):
        return requests.put(f"{BACKEND_URL}{endpoint}", json=data, headers=self._headers())

    def delete(self, endpoint: str):
        return requests.delete(f"{BACKEND_URL}{endpoint}", headers=self._headers())

api_session = APISession()