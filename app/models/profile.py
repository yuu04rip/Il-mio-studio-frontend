class Profile:
    def __init__(self, id, nome, cognome, email, numeroTelefonico, ruolo):
        self.id = id
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.numeroTelefonico = numeroTelefonico
        self.ruolo = ruolo

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            nome=d.get("nome"),
            cognome=d.get("cognome"),
            email=d.get("email"),
            numeroTelefonico=d.get("numeroTelefonico"),
            ruolo=d.get("ruolo"),
        )