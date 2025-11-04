class DipendenteTecnico:
    def __init__(self, id, nome, cognome, email, numeroTelefonico, ruolo, servizi=None, is_deleted=False):
        self.id = id
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.numeroTelefonico = numeroTelefonico
        self.ruolo = ruolo
        self.servizi = servizi or []
        self.is_deleted = is_deleted

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            nome=d.get("nome"),
            cognome=d.get("cognome"),
            email=d.get("email"),
            numeroTelefonico=d.get("numeroTelefonico"),
            ruolo=d.get("ruolo"),
            servizi=d.get("servizi", []),
            is_deleted=d.get("is_deleted", False),
        )