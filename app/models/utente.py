class Utente:
    def __init__(self, id, nome, cognome, email, numero_telefono, password, ruolo):
        self.id = id
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.numero_telefono = numero_telefono
        self.password = password
        self.ruolo = ruolo
    def get_nome(self):
        return self.nome
    def get_cognome(self):
        return self.cognome
    def get_email(self):
        return self.email
    def get_numero_telefono(self):
        return self.numero_telefono
    def get_password(self):
        return self.password
    def get_ruolo(self):
        return self.ruolo
    def get_id(self):
        return self.id
    def get_credenziali(self):
        return {
            "email": self.email,
            "password": self.password
        }
    def modifica_account(self, nome, cognome, email, numero_telefono, password):
        if nome: self.nome = nome
        if cognome: self.cognome = cognome
        if email: self.email = email
        if numero_telefono: self.numero_telefono = numero_telefono
        if password: self.password = password

