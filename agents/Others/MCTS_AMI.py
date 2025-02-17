from time import time
from copy import deepcopy
import socket
import random
import sys
import math
import logging

class MCTSNode:
    def __init__(self, state, color_to_move, mcts_color, parent=None):
        """
        Initialises new node

        Args:
            state (): State of the board
            color_to_move (str): Color of the player whose turn it is
            mcts_color (str): Color of the player using MCTS, used to count wins
            random (random): Random number generator
            parent (MCTSNode, optional): Parent node, defaults to None
        """

        self.state = state
        self.move = None # Saves the move that has been taken in this node
        self.parent = parent
        self.color_to_move = color_to_move
        self.mcts_color = mcts_color
        self.children = [] # child board states

        self.turn_count = 0
        self.eval_count = 0

        self.no_visits = 0
        self.no_wins = 0

        self.untried_moves = [] # moves that can still be tried
        for i in range(len(self.state)):
            for j in range(len(self.state[i])):
                if self.state[i][j] == 0:
                    self.untried_moves.append((i, j))

    def expand(self):
        """
        Expands the current node by creating a new child node

        Returns:
            MCTSNode: Child node containing the board with a next move
        """
        # get a new move from the untried_moves list
        move = self.untried_moves.pop()

        # create a new board state with the new move
        next_board = deepcopy(self.state)
        next_board[move[0]][move[1]] = self.color_to_move

        # create a new node with the new board state and add that to the children list
        new_child = MCTSNode(next_board, self.get_opp_colour(self.color_to_move), self.mcts_color, self)
        new_child.move = move
        self.children.append(new_child)

        return new_child
    
    def ln(self, x):
        n = 100000
        return n * ((x ** (1/n)) - 1)
    
    def get_neighbours(self, i, j):
        I_DISPLACEMENTS = [-1, -1, 0, 1, 1, 0]
        J_DISPLACEMENTS = [0, 1, 1, 0, -1, -1]

        neighbour_list = []

        for di, dj in zip(I_DISPLACEMENTS, J_DISPLACEMENTS):
            if 0 <= i + di < len(self.state) and 0 <= j + dj < len(self.state):
                neighbour_list.append((i + di, j + dj))

        return neighbour_list
    
    def get_opp_colour(self, colour):
        if colour == "R":
            return "B"
        elif colour == "B":
            return "R"
        else:
            return "None"
        
    def get_ucb_score(self, exploration_factor=1.41):
        if self.no_visits == 0:
            return sys.maxsize
        score = (self.no_wins / self.no_visits) + \
            exploration_factor * (math.log(self.no_visits) / self.no_visits) ** 0.5
        return score
    
    def check_win(self, state, player):
        visited = [[False for _ in range(len(state))] for _ in range(len(state))]

        def dfs(i, j):
            if i < 0 or i >= len(state) or j < 0 or j >= len(state) or state[i][j] != player or visited[i][j]:
                return False
            if (player == 'R' and i == len(state) - 1) or (player == 'B' and j == len(state) - 1):
                return True
            visited[i][j] = True
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, -1), (-1, 1)]
            return any(dfs(i + di, j + dj) for di, dj in directions)

        # For player 'R', check for a path from the top edge to the bottom edge
        if player == 'R':
            return any(dfs(0, j) for j in range(len(state)))
        
        # For player 'B', check for a path from the left edge to the right edge
        return any(dfs(i, 0) for i in range(len(state)))

    def best_child(self, exploration_factor):

        return max(self.children, key=lambda node: node.no_wins / (node.no_visits + 1e-4) +
                exploration_factor * math.sqrt(math.log(self.no_visits + 1) / (node.no_visits + 1e-4)))


    def rollout(self):
        """
        Randomly plays out the game from the current node until the end

        Returns:
            bool: whether the player won the game
        """
        current_state = deepcopy(self.state)
        current_color = deepcopy(self.color_to_move)

        # get random order of moves
        moves = []
        for i in range(len(current_state)):
            for j in range(len(current_state[i])):
                if current_state[i][j] == 0:
                    moves.append((i, j))

        random.shuffle(moves)

        while len(moves) > 0:
            move, moves = moves[0], moves[1:]
            current_state[move[0]][move[1]] = current_color
            current_color = self.get_opp_colour(current_color)
        
        return self.check_win(current_state, self.mcts_color)
    
    def backpropagate(self, winner):
        """
        Walks back to the root and updates visit and win values
        
        Args:
            winner (bool): Whether the player won the game
        """

        self.no_visits += 1
        if winner:
            self.no_wins += 1
        if self.parent:
            self.parent.backpropagate(winner)

    def is_leaf(self):
        """
        Checks if the node is a leaf, because it means end of game

        Returns:
            bool: Whether previous player already won the game
        """
        return self.check_win(self.state, self.get_opp_colour(self.color_to_move))
    
    def fully_expanded(self):
        """
        Checks if the node is fully expanded

        Returns:
            bool: Whether all moves have been tried
        """

        return len(self.untried_moves) == 0

class MCTSPlayer:
    HOST = "127.0.0.1"
    PORT = 1234

    # Manipulate the max_time_seconds here
    def __init__(self, board_size=11, max_time_seconds=6, no_simulations=1000000, exploration_factor=1.41):

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))

        self.board_size = board_size
        self.board = [[0] * self.board_size for _ in range(self.board_size)]
        self.colour = ""
        self.turn_count = 0

        ## for MCTS
        self.eval_count = 0
        self.max_time_seconds = max_time_seconds
        self.no_simulations = no_simulations 
        self.exploration_factor = exploration_factor
        self.turn_time = None

        self.root = None

    def run(self):
        while True:
            data = self.s.recv(1024)
            if not data:
                break
            if self.interpret_data(data):
                break

    def interpret_data(self, data):
        messages = data.decode("utf-8").strip().split("\n")
        messages = [x.split(";") for x in messages]

        for s in messages:
            if s[0] == "START":
                self.board_size = int(s[1])
                self.colour = s[2]
                self.board = [[0] * self.board_size for _ in range(self.board_size)]

                if self.colour == "R":
                    self.make_move()

            elif s[0] == "END":
                return True

            elif s[0] == "CHANGE":
                if s[3] == "END":
                    return True

                elif s[1] == "SWAP":
                    self.colour = self.opp_colour()
                    if s[3] == self.colour:
                        self.make_move()

                elif s[3] == self.colour:
                    action = [int(x) for x in s[1].split(",")]
                    self.board[action[0]][action[1]] = self.opp_colour()

                    self.make_move()

        return False
    
    def opp_colour(self):
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"
    
    def mcts(self):
        """
        Performs the MCTS
        
        Returns:
            MCTSNode: Best child node
        """
        self.root = MCTSNode(self.board, self.colour, self.colour)
        iter_count = 0

        while self.time_left() and iter_count < self.no_simulations:
            node = self.select()
            winner = node.rollout()
            node.backpropagate(winner)
            iter_count += 1

        self.eval_count += iter_count

        print(f"UCT root score Best Move: {self.root.get_ucb_score()}")
        print(
            f"Visits: {self.root.no_visits} | Wins: {self.root.no_wins}"
        )
        return self.root.best_child(exploration_factor=0)
    
    def select(self):
        """
        Selects the best child node to expand

        Returns:
            MCTSNode: Best child node
        """
        current_node = self.root
        while not current_node.is_leaf():
            if not current_node.fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child(self.exploration_factor)
        return current_node
    
    def time_left(self):
        """
        Checks if there is still time left to perform MCTS

        Returns:
            bool: Whether there is still time left
        """
        return time() - self.turn_time < self.max_time_seconds
    
    def make_move(self):
        """
        Makes a move using MCTS
        """
        self.turn_time = time()
        best_child = self.mcts()
        print(f"Total Playouts: {self.root.no_visits}")
        print(
            f"Best move selected: {best_child.move} | Visits: {best_child.no_visits} | Wins: {best_child.no_wins}"
        )
        print(f"UCT score Best Move: {best_child.get_ucb_score()}")
        self.s.sendall(
            bytes(f"{best_child.move[0]},{best_child.move[1]}\n", "utf-8")
        )
        self.board[best_child.move[0]][best_child.move[1]] = self.colour
        self.turn_count += 1

if __name__ == "__main__":
    player = MCTSPlayer()
    player.run()