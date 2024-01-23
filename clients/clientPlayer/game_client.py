# Seção de Importações
import pygame
from wall import Wall
from player import Player
import client_stub

"""
A grelha agora é construída com base no número de quadrados em x e y.
Isso nos permite associar o tamanho do espaço a uma matriz ou a um dicionário
que manterá os dados sobre cada posição no ambiente.
Além disso, agora podemos controlar o movimento dos objetos.
Agora separamos o controlo do ambiente
"""


class GameUI(object):
    def __init__(self, stub: client_stub.StubClient, player_id, player_name, grid_size: int = 20):
        dim: tuple = stub.dimension_size()
        self.x_max = dim[0]
        self.y_max = dim[1]
        self.stub = stub
        self.width, self.height = self.x_max * grid_size, self.y_max * grid_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Labyrinth Runners 2 - Player: " + player_name)
        self.clock = pygame.time.Clock()
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.grid_size = grid_size
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(self.white)
        self.screen.blit(self.background, (0, 0))

        self.player_id = player_id
        self.player_name = player_name
        self.players = pygame.sprite.LayeredDirty()
        self.players_dict = {}
        self.visited_y_coords = set()

        self.draw_grid(self.black)
        self.last_player_y = 0

    def draw_grid(self, colour: tuple):
        current_player_y = None
        if self.player_id in self.players_dict:
            current_player_y = self.players_dict[self.player_id].rect.y // self.grid_size

        for x in range(0, self.x_max):
            for y in range(0, self.y_max):
                # Always draw the exterior walls
                if x == 0 or y == 0 or x == self.x_max - 1 or y == self.y_max - 1:
                    pygame.draw.line(self.screen, colour, (x * self.grid_size, y * self.grid_size),
                                     ((x + 1) * self.grid_size, y * self.grid_size))
                    pygame.draw.line(self.screen, colour, (x * self.grid_size, y * self.grid_size),
                                     (x * self.grid_size, (y + 1) * self.grid_size))
                elif current_player_y is not None and (y in self.visited_y_coords or
                                                       y == current_player_y or
                                                       y == current_player_y - 1 or
                                                       y == current_player_y + 1):
                    # Draw grid lines for visited, current, and adjacent Y-coordinates
                    pygame.draw.line(self.screen, colour, (x * self.grid_size, y * self.grid_size),
                                     ((x + 1) * self.grid_size, y * self.grid_size))
                    pygame.draw.line(self.screen, colour, (x * self.grid_size, y * self.grid_size),
                                     (x * self.grid_size, (y + 1) * self.grid_size))
                else:
                    # Draw darkness for unvisited cells
                    dark_surface = pygame.Surface((self.grid_size, self.grid_size))
                    dark_surface.set_alpha(255)  # Adjust alpha for darkness intensity
                    dark_surface.fill((0, 0, 0))  # Black color
                    self.screen.blit(dark_surface, (x * self.grid_size, y * self.grid_size))

    def set_players(self):
        """
        Coloca os jogadores no ecrã
        :return: None
        """
        self.pl = self.stub.get_players()
        nr_players = self.stub.get_nr_players()

        existing_players = list(self.pl.keys())  # Get the existing player numbers

        for nr in range(nr_players):
            if nr in existing_players:
                p_x, p_y = self.pl[nr][1][0], self.pl[nr][1][1]
                if nr not in self.players_dict:  # This player is new
                    player = Player(nr, self.pl[nr][0], p_x, p_y, self.grid_size)
                    self.players_dict[nr] = player  # Store the player object in self.players_dict
                else:
                    player = self.players_dict[nr]  # This player already exists
                    # Here, you can update player's attributes if needed
                self.players.add(player)
            else:
                # Player disconnected, remove from self.pl and self.players_dict
                self.pl.pop(nr, None)
                if nr in self.players_dict:
                    self.players_dict.pop(nr)

        print(f"Players: {self.pl}")

    def set_walls(self, wall_size: int):
        """
        Desenha as paredes no ecrã
        :param wall_size: Tamanho das paredes
        :return: None
        """
        self.wl = self.stub.get_obstacles()
        # Cria as paredes (sprites) ao redor do mundo
        self.walls = pygame.sprite.Group()
        nr_obstacles = self.stub.get_nr_obstacles()
        for nr in range(nr_obstacles):
            if self.wl[nr]:
                w_x, w_y = self.wl[nr][1][0], self.wl[nr][1][1]
                wall = Wall(w_x, w_y, self.grid_size, self.walls)
                self.walls.add(wall)

    def draw_finish(self, image_path):
        """Desenha a imagem final(portal)"""
        x, y = self.finish_cell
        finish_image = pygame.image.load(image_path)
        finish_image = pygame.transform.scale(finish_image, (self.grid_size, self.grid_size))
        self.screen.blit(finish_image, (x * self.grid_size, y * self.grid_size))

    def run(self):
        """
        Inicializa o jogo
        :return: Verdadeiro se o jogo terminou com sucesso, falso caso contrário.
        """

        window = pygame.display.get_surface()
        window_size = window.get_size()
        width, height = window_size

        self.set_walls(self.grid_size)
        self.walls.draw(self.screen)
        self.set_players()
        end = False
        nr_players = self.stub.get_nr_players()

        # O mundo é atualizado constantemente
        world = dict()

        self.finish_cell = self.stub.get_finish()

        while not end:

            game_over, winner = self.stub.get_game_status()

            # Update visited Y-coordinates
            for player in self.players_dict.values():
                player_y = player.rect.y // self.grid_size
                self.visited_y_coords.update({player_y, player_y - 1, player_y + 1})

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Enviar informação "desconectado"
                    # Se a resposta for ok, então end é verdadeiro
                    end = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Enviar informação "desconectado"
                    # Se a resposta for ok, então end é verdadeiro
                    end = True

            # Get the current Y-coordinate of the player
            new_y = self.players_dict[self.player_id].rect.y // self.grid_size

            # Check if the player has moved down and request maze data
            if new_y > self.last_player_y:
                self.stub.request_maze()
                self.last_player_y = new_y

            new_nr_players = self.stub.get_nr_players()
            if new_nr_players > nr_players:
                for nr in range(nr_players, new_nr_players):
                    if nr in self.pl and self.pl[nr] != []:
                        p_x, p_y = self.pl[nr][1][0], self.pl[nr][1][1]
                        player = Player(nr, self.pl[nr][0], p_x, p_y, self.grid_size, self.players)
                        self.players.add(player)
                nr_players = new_nr_players

            if not game_over:
                self.walls.draw(self.screen)
                if self.finish_cell is not None:
                    self.draw_finish(r"pictures/portal.png")
                self.players.update(self.stub)
                self.players.draw(self.screen)
                self.draw_grid(self.black)
                pygame.display.flip()
                self.players.clear(self.screen, self.background)
                self.screen.fill((200, 200, 200))

            else:
                if self.player_id == self.stub.get_game_status()[1]:
                    message = f"{self.player_name}, congratulations you won!"
                else:
                    message = "You lost!"
                font = pygame.font.Font(None, 36)
                self.screen.fill((56, 5, 7))
                text = font.render(message, True, (255, 255, 255))
                text_rect = text.get_rect(center=(width // 2, height // 2))
                self.screen.blit(text, text_rect)
                pygame.display.flip()
        return True
