class Accettazione:
    def __init__(self, id, servizio_id, dipendente_id, stato, data_accettazione=None):
        self.id = id
        self.servizio_id = servizio_id
        self.dipendente_id = dipendente_id
        self.stato = stato
        self.data_accettazione = data_accettazione

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            servizio_id=d.get("servizio_id"),
            dipendente_id=d.get("dipendente_id"),
            stato=d.get("stato"),
            data_accettazione=d.get("data_accettazione"),
        )