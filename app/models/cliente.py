from utente import Utente
from documentazione import Documentazione
from servizio import Servizio
class Cliente:
    def __init__(self, utente, id,  documentazione=None, serviziRichiesti=None):
        self.utente = Utente(**utente)
        self.documentazione = documentazione
        self.serviziRichiesti = serviziRichiesti
    def aggiungiDocumentazione(self, documentazione):
        self.documentazione.append(documentazione)
    def mostraLavoriPerServizio(self, servizio    ):
        return self.serviziRichiesti(servizio).visualizzaLavoro()
    def sostituisciDocumentazione(self, documentazioneDaSostituire):
        index= self.documentazione.index(documentazioneDaSostituire)
        self.documentazione[index] = documentazioneDaSostituire
    def visualizzaDocumentazione(self):
        return self.documentazione.visualizzaDocumento()
