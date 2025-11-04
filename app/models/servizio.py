class Servizio:
    def __init__(
            self,
            id,
            cliente_id,
            codiceCorrente,
            codiceServizio,
            dataConsegna,
            dataRichiesta,
            statoServizio,
            tipo,
            is_deleted=False,
            lavoroCaricato=None,
            dipendenti=None,
    ):
        self.id = id
        self.cliente_id = cliente_id
        self.codiceCorrente = codiceCorrente
        self.codiceServizio = codiceServizio
        self.dataConsegna = dataConsegna
        self.dataRichiesta = dataRichiesta
        self.statoServizio = statoServizio
        self.tipo = tipo
        self.is_deleted = is_deleted
        self.lavoroCaricato = lavoroCaricato or []
        self.dipendenti = dipendenti or []

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get("id"),
            cliente_id=d.get("cliente_id"),
            codiceCorrente=d.get("codiceCorrente"),
            codiceServizio=d.get("codiceServizio"),
            dataConsegna=d.get("dataConsegna"),
            dataRichiesta=d.get("dataRichiesta"),
            statoServizio=d.get("statoServizio"),
            tipo=d.get("tipo"),
            is_deleted=d.get("is_deleted", False),
            lavoroCaricato=d.get("lavoroCaricato", []),
            dipendenti=d.get("dipendenti", []),
        )