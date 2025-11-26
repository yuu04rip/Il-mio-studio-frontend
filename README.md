# Il-mio-studio-frontend

Frontend dell’applicazione “Il mio studio”, sviluppato in **Python** con **NiceGUI** (UI web) e integrazione con il backend FastAPI  
(vedi repo backend: [Il-mio-studio-backend](https://github.com/yuu04rip/Il-mio-studio-backend)).

---

## 🏗️ Struttura del progetto

```text
Il-mio-studio-frontend/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── .idea/
├── .vscode/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── api.py                      # wrapper per chiamate REST al backend
│   ├── components/
│   │   ├── __init__.py
│   │   └── components.py               # componenti UI riutilizzabili (header, footer, ecc.)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── accettazione.py
│   │   ├── cliente.py
│   │   ├── dipendente_tecnico.py
│   │   ├── documentazione.py
│   │   ├── notaio.py
│   │   ├── profile.py
│   │   ├── servizio.py
│   │   └── utente.py                   # modelli/dto lato frontend
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── auth.py                     # pagina login/registrazione
│   │   ├── documentazione_servizio_page.py
│   │   ├── home.py                     # home / landing dopo login
│   │   ├── account/
│   │   │   ├── __init__.py
│   │   │   ├── account.py              # pagina profilo/account
│   │   │   ├── account_email.py        # cambio email
│   │   │   ├── account_mostra.py       # visualizzazione dati account
│   │   │   ├── account_password.py     # cambio password
│   │   │   └── logout.py               # logout utente
│   │   ├── cliente/
│   │   │   ├── __init__.py
│   │   │   ├── chatbox.py
│   │   │   ├── documentazione.py
│   │   │   ├── documentazione_servizio_cliente_page.py
│   │   │   ├── pagamento.py
│   │   │   ├── servizio_cliente_dettagli_page.py
│   │   │   └── servizi_cliente.py      # dashboard e flusso cliente
│   │   ├── dipendente/
│   │   │   ├── __init__.py
│   │   │   ├── clienti_dipendente.py
│   │   │   ├── servizi.py
│   │   │   └── servizio_dettagli_page.py
│   │   └── notaio/
│   │       ├── __init__.py
│   │       ├── accettazione.py
│   │       ├── archiviazione.py
│   │       ├── clienti.py
│   │       ├── dipendenti.py
│   │       └── servizio_dettagli_page_notaio.py
└── static/
    └── ...                             # asset statici (css, img, js) se presenti
```

---

## 🚀 Come avviare il progetto in locale

> Il frontend è progettato per lavorare insieme al backend  
> [Il-mio-studio-backend](https://github.com/yuu04rip/Il-mio-studio-backend).  
> Assicurati di avere il backend in esecuzione (es. su `http://localhost:8000`)
> prima di provare i flussi che chiamano le API.

### 1. Requisiti

- **Python 3.11+** (consigliato usare la stessa versione usata nel backend)
- `pip` aggiornato
- Facoltativo ma consigliato: ambiente virtuale (`venv`)

### 2. Clona la repository

```bash
git clone https://github.com/yuu04rip/Il-mio-studio-frontend.git
cd Il-mio-studio-frontend
```

### 3. (Consigliato) Crea e attiva un ambiente virtuale

**Su Windows (PowerShell):**
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

**Su macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Installa le dipendenze

Assicurati che l’ambiente virtuale sia attivato, poi:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Se durante l’installazione qualche pacchetto fallisce (es. problemi con `bcrypt` o librerie di sistema), installa prima le librerie richieste dalla tua piattaforma (ad es. `build-essential`, `libffi-dev`, ecc. su Linux) e ripeti il comando.

### 5. Configura eventuali variabili d’ambiente

Se il frontend deve chiamare il backend con un URL configurabile (es. `BACKEND_URL`), puoi:

- creare un file `.env` nella root, oppure
- impostare variabili d’ambiente nel tuo sistema / IDE.

Esempio `.env` (backend in locale):

```env
BACKEND_URL=http://localhost:8000
```

Controlla in `app/api/api.py` se legge qualche variabile d’ambiente o URL hard-coded, così sai cosa personalizzare.

### 6. Avvia l’applicazione

Dalla root del progetto:

```bash
python main.py
```

Oppure, se usi direttamente NiceGUI con `uvicorn` (se configurato così nel progetto):

```bash
uvicorn main:app --reload
```

Dopo l’avvio:

- Apri il browser su [http://localhost:8080](http://localhost:8080) oppure sulla porta indicata in console (dipende dalla configurazione di NiceGUI / FastAPI).

---
| Ruolo      | Email                                               | Password        | Note aggiuntive                |
| ---------- | --------------------------------------------------- | --------------- | ------------------------------ |
| Dipendente | [dipendente@gmail.com](mailto:dipendente@gmail.com) | le0p0ld0        |                                |
| Notaio     | [notaio3@studio.it](mailto:notaio3@studio.it)       | password_sicura | codice notarile: 1000          |
| Cliente    | [cliente@gmail.com](mailto:cliente@gmail.com)       | le0p0ld0        |                                |

---
## 🧪 Come testare velocemente che tutto funzioni

1. Verifica che l’app si avvii senza errori nel terminale.
2. Prova il flusso base:
    - apri `/` (home / login),
    - esegui un login con le credenziali di test (se fornite dal backend),
    - naviga tra:
        - pagina account (`/account/...`),
        - dashboard cliente (`/cliente/...`),
        - dashboard dipendente (`/dipendente/...`),
        - dashboard notaio (`/notaio/...`).
3. Se il backend è in esecuzione su un’altra porta/macchina, verifica che le chiamate API da `app/api/api.py` puntino all’URL corretto.

---

## 🛠️ Flusso di lavoro per collaborare in team

### 1. Clona la repository

```bash
git clone https://github.com/yuu04rip/Il-mio-studio-frontend.git
cd Il-mio-studio-frontend
```

---

### 2. Crea la tua branch personale

Lavora sempre su una branch separata per la tua parte/feature.  
**Esempi di nomi branch:**
- `feature/login-mario`
- `feature/dashboard-giulia`
- `feature/profile-riccardo`

**Comando:**
```bash
git checkout -b feature/nome-feature-tuo-nome
```

---

### 3. Sviluppa e fai commit sulla tua branch

- Lavora solo sulla tua branch.
- Fai commit frequenti e dai messaggi **chiari e descrittivi** (es: `fix: validazione email nel login`).
- **NON lavorare mai direttamente su `main`**!

---

### 4. Apri una Pull Request (PR) quando hai finito

- Dopo aver fatto il push della branch:
    - Su IntelliJ: “Create Pull Request” quando compare.
    - Oppure: **Git → GitHub → Create Pull Request**.
    - Oppure: Vai su GitHub → “Compare & pull request”.
- Seleziona la tua branch come “compare” e `main` come “base`.
- Scrivi **titolo** e **descrizione** (spiega cosa hai fatto!).
- Clicca “Create Pull Request” per inviare la PR.

L’admin (`yuu04rip`) controllerà la PR, può chiedere modifiche oppure approvare e fare il merge.

---

### 5. Solo l’admin può fare merge su `main`

- Nessuno deve mergiare su `main` senza approvazione dell’admin.
- Se vengono richieste modifiche, aggiorna la tua branch (push) e la PR si aggiorna in automatico.

---

### 6. Ripeti per ogni nuova funzionalità

- Dopo il merge, crea una nuova branch per la prossima feature.
- Segui sempre lo stesso flusso.

---
### 7. Test
Smoke test su main.py e su APIClient.
```bash
pytest app/tests -vv
```

---
## 📋 Regole base di collaborazione

- Branch dedicate per ogni persona/feature.
- PR **obbligatorie** per ogni modifica importante.
- L’admin revisiona tutto prima del merge.
- Se hai dubbi su come installare o su come far partire il progetto, chiedi prima di modificare file critici.

---

**Buon lavoro e buon sviluppo!**
