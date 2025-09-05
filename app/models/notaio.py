from utente import Utente

class Notaio:
    def __init__(self, utente, codiceNotarile):
        self.utente = Utente(**utente)
        self.codiceNotarile = codiceNotarile

     ## tutti i metodi si collegano al gestore