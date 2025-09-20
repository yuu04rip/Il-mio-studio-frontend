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
        resp = requests.post(f"{API_BASE}/studio/dipendenti", json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def add_notaio(self, user_data, codice_notarile):
        payload = user_data.copy()
        payload["codice_notarile"] = codice_notarile
        # Usa il nuovo endpoint
        resp = requests.post(f"{API_BASE}/auth/register-notaio", json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def elimina_dipendente(self, dipendente_id):
        """Soft delete: rimuove solo dalla lista, non dal db."""
        resp = requests.delete(f"{API_BASE}/studio/dipendente/{dipendente_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def distruggi_dipendente(self, dipendente_id):
        """Hard delete: elimina dal db."""
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

    # --- DOCUMENTAZIONE ---
    def carica_documentazione(self, cliente_id, tipo, filepath):
        url = f"{API_BASE}/studio/documenti/carica"
        files = {'file': open(filepath, 'rb')}
        data = {'cliente_id': cliente_id, 'tipo': tipo}
        resp = requests.post(url, data=data, files=files, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_documentazione(self, cliente_id):
        url = f"{API_BASE}/studio/documenti/visualizza/{cliente_id}"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def sostituisci_documentazione(self, doc_id, filepath):
        url = f"{API_BASE}/studio/documenti/sostituisci/{doc_id}"
        files = {'file': open(filepath, 'rb')}
        resp = requests.put(url, files=files, headers=self._headers())
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

    def crea_servizio(self, cliente_id, tipo, codiceCorrente, codiceServizio):
        url = f"{API_BASE}/studio/servizi"
        data = {
            "cliente_id": cliente_id,
            "tipo": tipo,
            "codiceCorrente": codiceCorrente,
            "codiceServizio": codiceServizio
        }
        resp = requests.post(url, data=data, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def cerca_servizio_per_codice(self, codice_servizio):
        resp = requests.get(f"{API_BASE}/studio/servizi/codice/{codice_servizio}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def elimina_servizio(self, servizio_id):
        """Soft delete: rimuove solo dalla lista servizi."""
        resp = requests.delete(f"{API_BASE}/studio/servizi/{servizio_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def distruggi_servizio(self, servizio_id):
        """Hard delete: elimina dal database."""
        resp = requests.delete(f"{API_BASE}/studio/servizi/{servizio_id}/distruggi", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def visualizza_servizi(self):
        resp = requests.get(f"{API_BASE}/studio/servizi/", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

