import os
import requests

API_BASE = "http://localhost:8000"

class APIClient:
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

    def post(self, url, data=None, **kwargs):
        full_url = f'{API_BASE}{url}' if url.startswith('/') else url
        return requests.post(full_url, data=data, headers=self._headers(), **kwargs)

    def get(self, endpoint: str):
        return requests.get(f"{API_BASE}{endpoint}", headers=self._headers())

    def put(self, endpoint: str, data: dict):
        return requests.put(f"{API_BASE}{endpoint}", json=data, headers=self._headers())

    def delete(self, endpoint: str):
        return requests.delete(f"{API_BASE}{endpoint}", headers=self._headers())

    def patch(self, endpoint: str, data: dict):
        return requests.patch(f"{API_BASE}{endpoint}", json=data, headers=self._headers())

    # --- AUTH ---
    def login(self, email, password):
        resp = requests.post(f"{API_BASE}/auth/login", json={"email": email, "password": password})
        resp.raise_for_status()
        data = resp.json()
        self.token = data["access_token"]
        return data

    def register(self, user_data):
        resp = requests.post(f"{API_BASE}/auth/register", json=user_data)
        resp.raise_for_status()
        data = resp.json()
        self.token = data["access_token"]
        return data

    def get_me(self):
        resp = requests.get(f"{API_BASE}/users/me", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    # --- DIPENDENTE / NOTAIO ---
    def register_dipendente(self, user_data):
        resp = requests.post(f"{API_BASE}/auth/register-dipendente", json=user_data)
        resp.raise_for_status()
        data = resp.json()
        self.token = data.get("access_token")
        return data

    def add_dipendente(self, user_data, tipo):
        payload = user_data.copy()
        payload["tipo"] = tipo
        resp = requests.post(f"{API_BASE}/studio/dipendenti", json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def add_notaio(self, user_data, codice_notarile):
        payload = user_data.copy()
        payload["codice_notarile"] = codice_notarile
        resp = requests.post(f"{API_BASE}/auth/register-notaio", json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def elimina_dipendente(self, dipendente_id):
        resp = requests.delete(f"{API_BASE}/studio/dipendente/{dipendente_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def distruggi_dipendente(self, dipendente_id):
        resp = requests.delete(f"{API_BASE}/studio/dipendente/{dipendente_id}/distruggi", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_lavoro_da_svolgere(self, dipendente_id):
        resp = requests.get(f"{API_BASE}/studio/dipendente/{dipendente_id}/servizi", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_servizi_inizializzati(self, dipendente_id):
        resp = requests.get(f"{API_BASE}/studio/dipendente/{dipendente_id}/servizi_inizializzati", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    # --- SERVIZI ---
    def archivia_servizio(self, servizio_id):
        resp = requests.post(f"{API_BASE}/studio/servizi/{servizio_id}/archivia", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def mostra_servizi_archiviati(self):
        resp = requests.get(f"{API_BASE}/studio/servizi/archiviati", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def modifica_servizio_archiviato(self, servizio_id, statoServizio: bool):
        resp = requests.put(
            f"{API_BASE}/studio/servizi/{servizio_id}/modifica-archiviazione",
            json={"statoServizio": statoServizio},
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def cerca_cliente_per_nome(self, nome):
        resp = requests.get(f"{API_BASE}/studio/clienti/nome/{nome}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def search_clienti(self, query):
        resp = requests.get(f"{API_BASE}/studio/clienti/search/", params={"q": query}, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def invia_chat_richiesta_servizio(self, cliente_id: int, testo: str):
        resp = requests.post(
            f"{API_BASE}/studio/servizi/richiesta-chat",
            json={"cliente_id": cliente_id, "testo": testo},
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def inizializza_servizio(self, servizio_id):
        resp = requests.post(
            f"{API_BASE}/studio/servizi/{servizio_id}/inizializza",
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def inoltra_servizio_notaio(self, servizio_id):
        resp = requests.post(
            f"{API_BASE}/studio/servizi/{servizio_id}/inoltra-notaio",
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def servizi_da_approvare(self):
        resp = requests.get(
            f"{API_BASE}/studio/notai/servizi",
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def approva_servizio(self, servizio_id):
        resp = requests.post(
            f"{API_BASE}/studio/servizi/{servizio_id}/approva",
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def rifiuta_servizio(self, servizio_id):
        resp = requests.post(
            f"{API_BASE}/studio/servizi/{servizio_id}/rifiuta",
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def assegna_servizio(self, servizio_id, dipendente_id):
        resp = requests.put(
            f"{API_BASE}/studio/servizi/{servizio_id}/assegna",
            json={"dipendente_id": dipendente_id},
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def crea_servizio(self, cliente_id, tipo, codice_corrente, dipendente_id):
        url = f"{API_BASE}/studio/servizi"
        data = {
            "cliente_id": int(cliente_id),
            "tipo": tipo,
            "codiceCorrente": int(codice_corrente),
            "dipendente_id": int(dipendente_id) if dipendente_id is not None else None
        }
        resp = requests.post(url, json=data, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def cerca_servizio_per_codice(self, codice_servizio):
        resp = requests.get(f"{API_BASE}/studio/servizi/codice/{codice_servizio}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def elimina_servizio(self, servizio_id):
        resp = requests.delete(f"{API_BASE}/studio/servizi/{servizio_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def distruggi_servizio(self, servizio_id):
        resp = requests.delete(f"{API_BASE}/studio/servizi/{servizio_id}/distruggi", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_servizi(self):
        resp = requests.get(f"{API_BASE}/studio/servizi/", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def get_dipendente_id_by_user(self, utente_id):
        resp = requests.get(f"{API_BASE}/studio/dipendente/by_user/{utente_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_servizi_completati(self, dipendente_id):
        resp = requests.get(f"{API_BASE}/studio/dipendente/{dipendente_id}/servizi_completati", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_servizi_finalizzati(self, dipendente_id):
        resp = requests.get(f"{API_BASE}/studio/dipendente/{dipendente_id}/servizi_finalizzati", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def get_altri_servizi(self, dipendente_id):
        url = f"{API_BASE}/studio/dipendenti/{dipendente_id}/altri_servizi"
        try:
            resp = requests.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            return []

    def carica_documentazione_servizio(self, servizio_id, tipo, filepath, filename=None):
        url = f"{API_BASE}/documentazione/servizi/{servizio_id}/documenti/carica"
        try:
            with open(filepath, "rb") as f:
                files = {"file": (filename or os.path.basename(filepath), f)}
                data = {"tipo": tipo}
                resp = requests.post(url, data=data, files=files, headers=self._headers())
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def visualizza_documentazione_servizio(self, servizio_id):
        url = f"{API_BASE}/documentazione/servizi/{servizio_id}/documenti"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def elimina_documentazione_servizio(self, servizio_id, doc_id):
        url = f"{API_BASE}/documentazione/servizi/{servizio_id}/documenti/{doc_id}"
        resp = requests.delete(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def sostituisci_documentazione_servizio(self, servizio_id, doc_id, filepath):
        url = f"{API_BASE}/documentazione/servizi/{servizio_id}/documenti/{doc_id}/sostituisci"
        files = {"file": open(filepath, "rb")}
        resp = requests.put(url, files=files, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def download_documentazione(self, doc_id):
        url = f"{API_BASE}/documentazione/download/{doc_id}"
        resp = requests.get(url, headers=self._headers(), stream=True)
        resp.raise_for_status()
        return resp.content

    def carica_documentazione_cliente(self, cliente_id, tipo, filepath):
        url = f"{API_BASE}/documentazione/documenti/carica"
        files = {"file": open(filepath, "rb")}
        data = {"cliente_id": cliente_id, "tipo": tipo}
        resp = requests.post(url, data=data, files=files, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_documentazione_cliente(self, cliente_id):
        url = f"{API_BASE}/documentazione/documenti/visualizza/{cliente_id}"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def sostituisci_documentazione_cliente(self, doc_id, filepath):
        url = f"{API_BASE}/documentazione/documenti/sostituisci/{doc_id}"
        files = {"file": open(filepath, "rb")}
        resp = requests.put(url, files=files, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_servizi_approvati(self):
        resp = requests.get(f"{API_BASE}/studio/servizi/approvati", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

api_session = APIClient()