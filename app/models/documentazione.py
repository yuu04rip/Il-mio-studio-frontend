class Documentazione:
    def __init__(self, id, cliente_id, filename, tipo, path, is_deleted=False, descrizione=None):
        self.id = id
        self.cliente_id = cliente_id
        self.filename = filename
        self.tipo = tipo
        self.path = path
        self.is_deleted = is_deleted
        self.descrizione = descrizione

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            cliente_id=d.get("cliente_id"),
            filename=d.get("filename"),
            tipo=d.get("tipo"),
            path=d.get("path"),
            is_deleted=d.get("is_deleted", False),
            descrizione=d.get("descrizione", None),
        )