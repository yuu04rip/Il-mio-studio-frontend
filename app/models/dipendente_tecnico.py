from cliente import Cliente
from utente import Utente
class DipendenteTecnico:
    def __init__(self, utente, id, clienti=None):
        self.utente = Utente(**utente)
        self.id = id
        self.clienti = clienti
    def __del__(self):
        print(f"Dipendente cancellato dal database.")
  ## mancano i metodi in relazione con i gestori