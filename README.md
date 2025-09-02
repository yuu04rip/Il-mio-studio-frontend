# invest-app-frontend

## 🛠️ Flusso di lavoro per collaborare in team

### 1. Clona la repository

```bash
git clone https://github.com/yuu04rip/invest-app-frontend.git
cd invest-app-frontend
```

---

### 2. Crea la tua branch personale

Ogni membro deve lavorare su una branch separata per la propria parte/feature.  
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
- Fai commit regolari con messaggi chiari.
- Non lavorare mai direttamente su `main`.

---

### 4. Apri una Pull Request (PR) quando hai finito

- **Consiglio:** Potete aprire la pull request direttamente da IntelliJ IDEA.
    - Dopo aver fatto il push della vostra branch, cliccate su “Create Pull Request” che appare in IntelliJ.
    - Oppure andate su **Git → GitHub → Create Pull Request**.
    - Selezionate la vostra branch come “compare” e `main` come “base”.
    - Scrivete titolo e descrizione della PR.
    - Confermate per inviare la PR.
- L’admin (yuu04rip) controllerà la PR, può chiedere modifiche oppure approvare e fare il merge.

---

### 5. Solo l’admin può fare merge su `main`

- Nessuno deve mergiare su `main` senza approvazione dell’admin.
- In caso di modifiche richieste, aggiornate la vostra branch e la PR si aggiorna automaticamente.

---

### 6. Ripeti per ogni nuova funzionalità

- Dopo il merge, create una nuova branch per la prossima feature.
- Il flusso rimane sempre uguale.

---

## 📋 Regole base

- Branch dedicate per ogni persona/feature.
- PR obbligatorie per ogni modifica importante.
- L’admin revisiona tutto prima del merge.
- Se hai dubbi, chiedi prima!

---

## 🛡️ Protezione branch (admin)

L’admin imposterà la protezione su `main`:
- Serve almeno una review prima del merge.
- Solo l’admin può approvare/mergiare.

---

**Buon lavoro!**
