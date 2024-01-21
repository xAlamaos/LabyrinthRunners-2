# Seção de Importações
import socket
import threading
from game_mech import GameMech
import const
from client_handler import ClientHandler


# Está no lado do servidor: Skeleton to ‘user’ ‘interface’ (permite ter informação de como comunicar com o cliente)
class SkeletonServer:
    def __init__(self, gm_obj: GameMech):
        """
        Construtor da classe 'SkeletonServer'
        :param gm_obj: Um objeto GameMech que representa o mecanismo do jogo
        """
        self.gm = gm_obj
        self.s = socket.socket()
        self.s.bind((const.ADDRESS, const.PORT))
        self.s.listen()
        self.stop = False

    def run(self):
        while not self.stop:
            socket_client, address = self.s.accept()
            print(f"Connection established with {address}")
            # Create an instance of the ClientHandler class and pass the clientPlayer socket
            client_handler = ClientHandler(self.gm)

            # Send the last maze file to the client
            client_handler.send_last_maze(socket_client)

            # Handle client in a separate thread
            client_thread = threading.Thread(target=client_handler.handle_client, args=(socket_client,))
            client_thread.start()

        self.s.close()
