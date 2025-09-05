from datetime import datetime, timedelta
from documentazione import Documentazione
from cliente import Cliente
from dipendente_tecnico import DipendenteTecnico
class Servizio:
    def __init__(self, id, dipendenteTecnico,dataCorrente, tipoServizio, Cliente=None, lavoroCaricato=None):
        self.id = id
        self.dipendenteTecnico = dipendenteTecnico
        self.Cliente = Cliente
        self.lavoroCaricato = lavoroCaricato
        self.dataCorrente = dataCorrente
        intervallo_giorni = timedelta(days=20)
        self.dataConsegna=dataCorrente + intervallo_giorni
        self.statoServizio= "INIZIALIZZATO"
        self.tipoServizio = tipoServizio
    def aggiungiLavoro (self, documentazione):
        self.lavoroCaricato.append(documentazione)
    def getIdServizio(self):
        return self.id
    def getDataCorrente(self):
        return self.dataCorrente
    def getDataConsegna(self):
        return self.dataConsegna
    def getInfoServizio(self):
        return self.tipoServizio & self.Cliente.get_nome()
    def getStatoServizio(self):
        return self.statoServizio
    def modificaLavoro(self, documentazione1, documentazione2):
        index=self.lavoroCaricato.index(documentazione1)
        self.lavoroCaricato[index] = documentazione2
    def setStatoServizio(self, statoServizio):
        self.statoServizio = statoServizio
    def visualizzaLavoro(self):
        return self.lavoroCaricato
    def __del__(self):
        print(f"Documento eliminato.")
    def get_nome_dipendentiTecnici(self):
        nomiDipendentiTempr=None
        for dipendente in self.dipendenteTecnico:
         nomiDipendentiTempr.append(dipendente)
        return nomiDipendentiTempr

