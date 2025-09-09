import requests

API_BASE = "http://localhost:8000"  # Cambia con l'URL reale del backend

class APIClient:
    def __init__(self):
        self.token = None

    def _headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

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
        resp = requests.get(f"{API_BASE}/me", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    # --- DIPENDENTE / NOTAIO ---
    def add_dipendente(self, user_data, tipo):
        payload = user_data.copy()
        payload["tipo"] = tipo
        resp = requests.post(f"{API_BASE}/add-dipendente", json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def add_notaio(self, user_data, codice_notarile):
        resp = requests.post(f"{API_BASE}/add-notaio?codice_notarile={codice_notarile}", json=user_data, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def distruggi_dipendente(self, dipendente_id):
        resp = requests.delete(f"{API_BASE}/dipendente/{dipendente_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_lavoro_da_svolgere(self, dipendente_id):
        resp = requests.get(f"{API_BASE}/dipendente/{dipendente_id}/servizi", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_servizi_inizializzati(self, dipendente_id):
        resp = requests.get(f"{API_BASE}/dipendente/{dipendente_id}/servizi_inizializzati", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    # --- DOCUMENTAZIONE ---
    def carica_documentazione(self, cliente_id, tipo, filepath):
        url = f"{API_BASE}/documentazione/carica"
        files = {'file': open(filepath, 'rb')}
        data = {'cliente_id': cliente_id, 'tipo': tipo}
        resp = requests.post(url, data=data, files=files, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_documentazione(self, cliente_id):
        url = f"{API_BASE}/documentazione/visualizza/{cliente_id}"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def sostituisci_documentazione(self, doc_id, filepath):
        url = f"{API_BASE}/documentazione/sostituisci/{doc_id}"
        files = {'file': open(filepath, 'rb')}
        resp = requests.put(url, files=files, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    # --- SERVIZI ---
    def archivia_servizio(self, servizio_id):
        resp = requests.post(f"{API_BASE}/archivia", json={"servizio_id": servizio_id}, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def mostra_servizi_archiviati(self):
        resp = requests.get(f"{API_BASE}/servizi/archiviati", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def modifica_servizio_archiviato(self, servizio_id, statoServizio: bool):
        resp = requests.put(
            f"{API_BASE}/servizi/archiviati/{servizio_id}",
            json={"statoServizio": statoServizio},
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def cerca_cliente_per_nome(self, nome):
        resp = requests.get(f"{API_BASE}/clienti/nome/{nome}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def inizializza_servizio(self, cliente_nome, tipo, codiceCorrente, codiceServizio):
        url = f"{API_BASE}/inizializza"
        data = {
            "cliente_nome": cliente_nome,
            "tipo": tipo,
            "codiceCorrente": codiceCorrente,
            "codiceServizio": codiceServizio
        }
        # FastAPI Form expects data in x-www-form-urlencoded
        resp = requests.post(url, data=data, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def cerca_servizio_per_codice(self, codice_servizio):
        resp = requests.get(f"{API_BASE}/servizi/codice/{codice_servizio}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def elimina_servizio(self, servizio_id):
        resp = requests.delete(f"{API_BASE}/servizi/{servizio_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_servizi(self):
        resp = requests.get(f"{API_BASE}/servizi/", headers=self._headers())
        resp.raise_for_status()
        return resp.json()