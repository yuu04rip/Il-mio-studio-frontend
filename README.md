# Il-mio-studio-frontend

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

- **Consiglio:** Potete aprire la pull request direttamente da IntelliJ IDEA o da GitHub.
    - Dopo aver fatto il push della branch:
        - Su IntelliJ: “Create Pull Request” quando compare.
        - Oppure: **Git → GitHub → Create Pull Request**.
        - Oppure: Vai su GitHub → “Compare & pull request”.
    - Seleziona la tua branch come “compare” e `main` come “base”.
    - Scrivi **titolo** e **descrizione** (spiega cosa hai fatto!).
    - Clicca “Create Pull Request” per inviare la PR.
- L’admin (`yuu04rip`) controllerà la PR, può chiedere modifiche oppure approvare e fare il merge.

---

### 5. Solo l’admin può fare merge su `main`

- **Nessuno deve mergiare su `main` senza approvazione dell’admin.**
- Se vengono richieste modifiche, aggiorna la tua branch (push) e la PR si aggiorna in automatico.

---

### 6. Ripeti per ogni nuova funzionalità

- Dopo il merge, crea una nuova branch per la prossima feature.
- Segui sempre lo stesso flusso.

---

## 📋 Regole base

- Branch dedicate per ogni persona/feature.
- PR **obbligatorie** per ogni modifica importante.
- L’admin revisiona tutto prima del merge.
- Se hai dubbi, **chiedi prima di fare danni!**

---

## 🗂️ Suddivisione delle responsabilità (consigliata)

Per tenere il lavoro ordinato, è utile suddividere le aree del frontend tra i membri del team.  
Ecco alcune **idee di suddivisione**:

### Esempio suddivisione:

- **Login/Registrazione/Autenticazione:**  
  _Responsabile: Mario_  
  File: `auth.py`, pagine login, register, recupero password  
  CSS: `auth-modern-card`, input, bottoni

- **Dashboard Cliente:**  
  _Responsabile: Giulia_  
  File: `home_cliente.py`, `account.py`, `documentazione.py`, `chatbox.py`  
  CSS: `glass-card`, `glass-title`, `glass-btn`

- **Dashboard Dipendente:**  
  _Responsabile: Luca_  
  File: `home_dipendente.py`, `clienti_page_dipendente.py`, `servizi_dipendente_page.py`  
  CSS: bottoni, card, input

- **Dashboard Notaio:**  
  _Responsabile: Riccardo_  
  File: `home_notaio.py`, `accettazione_notaio.py`, `servizio_dettagli_page_notaio.py`  
  CSS: card, bottoni, input

- **Componenti globali:**  
  _Responsabile: Team_  
  File: `components/`, header, footer, notifiche, dialog

- **API/Servizi:**  
  _Responsabile: Backend/frontend referenti_  
  File: `api/api.py`, test connessione, chiamate REST

> **Consiglio:** Scrivi sempre chi è responsabile di una sezione nei commenti dei file!  
> Esempio: `# Responsabile: Mario (login)` all’inizio del file.

---

## 🎨 Suggerimenti per modifiche grafiche (frontend)

- Ogni componente/pagina ha i suoi file Python (es. `account.py`, `cambia_email.py`).
- Per personalizzare la grafica:
    - Modifica le **classi CSS** nei file (es: `.glass-card`, `.glass-title`, `.glass-btn`).
    - Cambia i **colori**, **font**, **padding**, **border-radius** nei CSS in fondo ai file o nel file globale.
    - Puoi aggiungere CSS con `ui.add_head_html("""<style>...</style>""")` oppure creare un file `.css`.
    - Per aggiungere **icone**, usa `ui.icon('nome_icona')` (nomi da [Material Icons](https://fonts.google.com/icons)).
    - Per layout, usa `ui.row()`, `ui.column()`, `ui.card()`, `ui.button()`, ecc.
    - Per dialog/pop-up: `ui.dialog()`.
    - Per aggiungere HTML/CSS/JS custom: `ui.add_head_html`, `ui.add_body_html`, `ui.add_js_file`, `ui.add_css_file`.
    - **Commenta le sezioni che modifichi** così il team capisce subito dove intervenire!
    - Consulta la [documentazione NiceGUI](https://nicegui.io/documentation) per esempi e props.

---

## 🛡️ Protezione branch (admin)

L’admin imposta la protezione su `main`:
- Serve almeno **una review** prima del merge.
- Solo l’admin può approvare/mergiare.

---

**Buon lavoro e buona collaborazione!**