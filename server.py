import socket
import threading
import base64

def get_ip():
    """
    Récupère l'adresse IP locale de la machine.
    Input : 
        /
    Output :
        str : L'adresse IP locale de la machine. Retourne "127.0.0.1" si hors réseau.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip
    
    
def keygen(chaine: str) -> str:
    """
    Génère une clé encodée en Base64 à partir d'une chaîne d'entrée.

    Input :
        chaine : Une chaîne de caractères à encoder.
        Pré-cond: chaine de type str
    Output :
        str : La chaîne encodée en Base64.
    """
    return base64.b64encode(chaine.encode()).decode()
    
    
def keygenRev(key: str) -> str:
    """
    Décode une clé encodée en Base64.

    Input :
        key : Une chaîne encodée en Base64.
        Pré-cond : key de type str

    Retourne :
        str : La clé décodée.
    """
    return base64.b64decode(key.encode()).decode()


class ChatServer:
    """
    Classe représentant un serveur de chat.

    Attributs :
        host (str) : Adresse IP sur laquelle le serveur écoute.
        port (int) : Port sur lequel le serveur écoute.
        server (socket ou None) : Socket du serveur, initialisé lors de l'appel à start().
        clients (list) : Liste des sockets clients connectés.
        pseudo (list) : Liste des pseudonymes des clients connectés.
    """

    def __init__(self, host="192.168.1.66", port=5000):
        """
        Initialise une instance du serveur de chat.

        Input :
            host (str) : Adresse IP du serveur (par défaut "192.168.1.66").
            port (int) : Port du serveur (par défaut 5000).
        """
        self.host = host
        self.port = port
        self.server = None
        self.clients = []
        self.pseudo = []
	
	
    def getClients(self):
        """
        Récupère la liste des sockets des clients connectés.

        Output :
            list : Une liste contenant les sockets des clients connectés.
        """
        return self.clients
    
    def getPseudo(self):
        """
        Récupère la liste des pseudonymes des clients connectés.

        Output :
            list : Une liste contenant les pseudonymes des clients connectés.
        """
        return self.pseudo


    def handle_client(self, client_socket, address):
        """
        Gère la communication avec un client donné.

        Input :
            client_socket (socket) : Socket représentant le client.
            address (tuple) : Adresse (IP, port) du client.

        Fonctionnement :
            - Reçoit les messages du client.
            - Si le message contient un pseudonyme (préfixé par "pseudo$"), l'ajoute à la liste des pseudonymes.
            - Diffuse le message à tous les autres clients.
        """
        print(f"[NOUVEAU CLIENT] {address} connecté.")
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                
                if message:
                    if message.split("$")[0] == "pseudo":
                        self.pseudo.append(message.split("$")[1]) if message.split("$")[1] not in self.pseudo else None
                        print(self.pseudo)
                    self.broadcast(message, client_socket)
                else:
                    break
            except:
                break

        print(f"[DÉCONNECTÉ] {address} a quitté.")
        self.clients.remove(client_socket)
        client_socket.close()
    
    def send(self, message: str, destination):
        """
        Envoie un message à un client spécifique.

        Input :
            message (str) : Message à envoyer.
            destination (socket) : Socket du client destinataire.
            Pré-cond : message de type str
        """
        destination.send(message)
    	    
    def broadcast(self, message: str, sender_socket):
        """
        Diffuse un message à tous les clients connectés sauf l'expéditeur.

        Input :
            message (str) : Message à diffuser.
            sender_socket (socket) : Socket de l'expéditeur à exclure.
            Pré-cond : message de type str

        """
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    client.close()
                    self.clients.remove(client)

    def start(self):
        """
        Démarre le serveur de chat et accepte les connexions entrantes.

        Fonctionnement :
            - Configure le serveur pour écouter sur l'adresse IP et le port spécifiés.
            - Accepte les connexions des clients.
            - Lance un thread pour gérer chaque client connecté.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[DÉMARRÉ] Serveur en attente de connexions sur {self.host}:{self.port}...")

        while True:
            client_socket, client_address = self.server.accept()
            self.clients.append(client_socket)
            thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            thread.start()
