import math
import random
import time
import cProfile
from multiprocessing import Pool


def check_win(state, player_colour):
    size = len(state)
    visited = set()

    def dfs_iterative(start_nodes):
        stack = list(start_nodes)
        while stack:
            i, j = stack.pop()
            if (player_colour == 'R' and i == size - 1) or (player_colour == 'B' and j == size - 1):
                return True
            for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, -1), (-1, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < size and 0 <= nj < size and (ni, nj) not in visited and state[ni][nj] == player_colour:
                    visited.add((ni, nj))
                    stack.append((ni, nj))
        return False

    edge_cells = {(i, 0) for i in range(size)} if player_colour == 'B' else {(0, j) for j in range(size)}
    edge_cells = {(i, j) for i, j in edge_cells if state[i][j] == player_colour}

    return dfs_iterative(edge_cells)


class Node:
    def __init__(self, board, color_to_move = None, move=None, parent=None):
        # Initialize MCTS node
        self.board = board
        self.color_to_move = color_to_move
        self.move = move  # The move that led to this node
        self.parent = parent  # Parent node
        self.children = []  # Child nodes
        self.visits = 0  # Number of visits to this node
        self.wins = 0  # Number of wins from this node
        self.legal_moves = self.possibleMoves()
  
    def possibleMoves(self):
        moves = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == 0:
                    moves.append((i, j))
        return moves

    def expand(self):
        # print(f"Selected node move: {self.move}")
        # get random move from available moves
        move = self.legal_moves.pop()
        # create new board from the node with the new move
        next_board = [row[:] for row in self.board]  # Shallow copy of board
        next_board[move[0]][move[1]] = self.color_to_move

        # create new node with new board and add to children
        next_colour = 'B' if self.color_to_move == 'R' else 'R'
        new_child = Node(next_board, next_colour , move, self)
        self.children.append(new_child)

        return new_child
    
    def fully_expanded(self):
        return len(self.legal_moves) == 0

    def is_terminal(self):
        return check_win(self.board, 'B' if self.color_to_move == 'R' else 'R')
    
class MCTS:
    def __init__(self, color):
        self.root = None
        self.player_colour = color

    def determine_game_stage(self, board):
        empty_tiles = 0
        for row in board:
            for tile in row:
                if tile == 0:
                    empty_tiles += 1
        print(f"Empty tiles: {empty_tiles}")
        total_tiles = 121
        filled_ratio = (total_tiles - empty_tiles) / total_tiles
        print(f"Filled ratio: {filled_ratio}")

        # Early game: less than 30% of the board is filled
        # Mid game: 30% to 70% of the board is filled
        # Late game: more than 70% of the board is filled
        if filled_ratio < 0.3:
            return "early"
        elif filled_ratio < 0.7:
            return "mid"
        else:
            return "late"

    
    def run_mcts(self, board, time_limit, iterations=10000):
        if self.determine_game_stage(board) == "early":
            ammended_time = time_limit
        elif self.determine_game_stage(board) == "mid":
            ammended_time = int(time_limit * 1.5)
        else:
            ammended_time = int(time_limit * 2)
        start_time = time.time()
        # Initialize the root dynamically
        self.root = Node(board, self.player_colour)

        # Perform MCTS search to find the best move
        iter = 0
        # for _ in range(iterations):
        while time.time() - start_time < ammended_time:
            current_node = self.root
            # Selection
            current_node = self.select(current_node)

            # Parallel Simulation
            simulation_results = self.simulate(current_node)

            # Backpropagate
            self.backpropagate(current_node, simulation_results)
            iter+=1
        
        print(f"---------Group41------------")
        print(f"Completed {iter} iterations")
        best_node = max(self.root.children, key=lambda x: x.wins/x.visits)
        print(f"Best node ucb score {self.ucb_score(best_node)}")
        print(f"Move: {best_node.move}, Wins: {best_node.wins}, Visits: {best_node.visits}")
        print(f"---------Group41------------")
        best_move = best_node.move
        return best_move
    
    def select(self, node:Node):
        # do while loop till it get to leaf node
        while not node.is_terminal():
            if not node.fully_expanded():
                return node.expand()
            else:
                # get best child based on ucb score
                node = max(node.children, key=self.ucb_score)
        return node

    
    def simulate(self, node: Node):
        # Deep copy the board from the node to run a simulation
        current_board = [row[:] for row in node.board]  # Shallow copy of board
        possible_moves = node.legal_moves.copy()
        current_color = node.color_to_move

        random.shuffle(possible_moves)

        while possible_moves:
            move = random.choice(possible_moves)
            possible_moves.remove(move)
            current_board[move[0]][move[1]] = current_color
            current_color = 'B' if current_color == 'R' else 'R'

        return 1 if check_win(current_board, self.player_colour) else 0

    def backpropagate(self, node: Node, result):
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent
                  
    def ucb_score(self, node):
        # Calculate the UCB score for a given node
        if node.visits == 0:
            return float("inf")
        exploitation = node.wins / node.visits
        exploration = math.sqrt(2*math.log(node.parent.visits) / node.visits)
        return exploitation + exploration
    
    def print_tree(self, node: Node, depth=0):
        """Recursively print the tree hierarchy."""
        indent = "  " * depth
        print(f"{indent}{depth}. Move: {node.move}, Wins: {node.wins}, Visits: {node.visits}, colour_to_move: {node.color_to_move}")

        for child in node.children:
            self.print_tree(child, depth + 1)

    def print_child_root(self, node: Node):
        for child in node.children:
            print(f"    Move: {child.move}, Wins: {child.wins}, Visits: {child.visits}, win/visit: {child.wins/child.visits}")
        
if __name__ == "__main__":
    board_size = 11
    b = [[0 for _ in range(board_size)] for _ in range(board_size)]  # Empty board
    mcts = MCTS("R")

    # Profile the run_mcts method
    # cProfile.run('mcts.run_mcts(b, time_limit=6)')

    # If you want to use the result of run_mcts after profiling, call it again
    best_move = mcts.run_mcts(b, time_limit=10)
    print("Best Move:", best_move)
    mcts.print_child_root(mcts.root)
