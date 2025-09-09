class Utente:
    def __init__(self, id, email, nome, cognome, numeroTelefonico, ruolo):
        self.id = id
        self.email = email
        self.nome = nome
        self.cognome = cognome
        self.numeroTelefonico = numeroTelefonico
        self.ruolo = ruolo

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            email=d.get("email"),
            nome=d.get("nome"),
            cognome=d.get("cognome"),
            numeroTelefonico=d.get("numeroTelefonico"),
            ruolo=d.get("ruolo"),
        )

    # Getter e setter come da UML (opzionali in Python, qui per chiarezza)
    def getNome(self):
        return self.nome

    def getCognome(self):
        return self.cognome

    def getEmail(self):
        return self.email

    def getNumeroTelefonico(self):
        return self.numeroTelefonico

    def getRuolo(self):
        return self.ruolo

    def setNome(self, nome):
        self.nome = nome

    def setCognome(self, cognome):
        self.cognome = cognome

    def setEmail(self, email):
        self.email = email

    def setNumeroTelefonico(self, numeroTelefonico):
        self.numeroTelefonico = numeroTelefonico

    def setRuolo(self, ruolo):
        self.ruolo = ruolo