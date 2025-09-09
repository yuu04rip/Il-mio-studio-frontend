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