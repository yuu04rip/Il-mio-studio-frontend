class Cliente:
    def __init__(self, id, nome, cognome, email, servizi=None, is_deleted=False):
        self.id = id
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.servizi = servizi or []  # lista di Servizio
        self.is_deleted = is_deleted

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            nome=d.get("nome"),
            cognome=d.get("cognome"),
            email=d.get("email"),
            servizi=d.get("servizi", []),
            is_deleted=d.get("is_deleted", False),
        )