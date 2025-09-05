class Documentazione:
    def __init__(self,tipo, indirizzo, id, cliente_Id, documento):
        self.tipo = tipo
        self.indirizzo = indirizzo
        self.id = id
        self.cliente_Id = cliente_Id
        self.documento = documento
    def getTipo(self):
        return self.tipo
    def visualizzaDocumento(self):
        return self.documento


