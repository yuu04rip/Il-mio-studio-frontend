class Notaio:
    def __init__(self, id, utente, codice_notarile, is_deleted=False):
        self.id = id
        self.utente = utente  # dict o oggetto Utente
        self.codice_notarile = codice_notarile
        self.is_deleted = is_deleted

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            utente=d.get("utente"),
            codice_notarile=d.get("codice_notarile"),
            is_deleted=d.get("is_deleted", False),
        )