import random
import math


class SimulatedAnnealing:
    def __init__(self):
        self.temperature = 100  # Initial temperature, adjust as needed
        self.alpha = 0.95       # Cooling rate, adjust as needed
        self.steps = 100        # Number of steps at each temperature level

    def calculate_cost(self, path, goal):
        # Simple cost function: Euclidean distance from the last point in the path to the goal
        last_point = path[-1]
        return math.sqrt((last_point[0] - goal[0])**2 + (last_point[1] - goal[1])**2)

    def get_next_position(self, maze, current_position):
        # Choose a random neighboring cell that is not a wall
        x, y = current_position
        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        valid_neighbors = [pos for pos in neighbors if maze[pos[1]][pos[0]] == '0']
        return random.choice(valid_neighbors) if valid_neighbors else current_position

    def acceptance_probability(self, old_cost, new_cost):
        if new_cost < old_cost:
            return 1.0
        else:
            return math.exp((old_cost - new_cost) / self.temperature)

    def convert_path_to_moves(self, path):
        # Convert path coordinates into game moves
        moves = []
        for i in range(1, len(path)):
            x_diff = path[i][0] - path[i-1][0]
            y_diff = path[i][1] - path[i-1][1]
            if x_diff == 1:
                moves.append('right')
            elif x_diff == -1:
                moves.append('left')
            elif y_diff == 1:
                moves.append('down')
            elif y_diff == -1:
                moves.append('up')
        return moves

    def explore(self, maze, current_pos):
        # Logic to explore the maze and find unvisited cells
        return random.choice(['left', 'right', 'up', 'down'])  # Example

    def find_path(self, maze, start, goal):
        current_position = start
        current_path = [start]
        best_path = list(current_path)
        best_cost = self.calculate_cost(current_path, goal)

        while self.temperature > 1:
            for _ in range(self.steps):
                next_position = self.get_next_position(maze, current_position)
                new_path = current_path + [next_position]
                new_cost = self.calculate_cost(new_path, goal)

                if self.acceptance_probability(best_cost, new_cost) > random.random():
                    current_position = next_position
                    current_path = new_path
                    if new_cost < best_cost:
                        best_path = new_path
                        best_cost = new_cost

            self.temperature *= self.alpha

        return self.convert_path_to_moves(best_path)
