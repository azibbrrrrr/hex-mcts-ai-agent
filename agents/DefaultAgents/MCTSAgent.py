import math
import random

class node:
    def __init__(self, move=None, parent=None):
        # Initialize MCTS node
        self.move = move  # The move that led to this node
        self.parent = parent  # Parent node
        self.children = []  # Child nodes
        self.visits = 0  # Number of visits to this node
        self.wins = 0  # Number of wins from this node

def ucb_score(node):
    # Calculate the UCB score for a given node
    if node.visits == 0:
        return float("inf")
    exploitation = node.wins / node.visits
    exploration = math.sqrt(2 * math.log(node.parent.visits) / node.visits)
    return exploitation + exploration

def select_child(node):
    # Select a child node based on UCB scores
    return max(node.children, key=ucb_score)

def expand(node, game):
    # Expand the tree by adding child nodes
    legal_moves = game.legal_moves()
    for move in legal_moves:
        new_node = node(move, node)
        node.children.append(new_node)
    return random.choice(node.children)

def simulate(game):
    # Simulate a random game and return the result
    # This could be replaced with a more sophisticated simulation based on game rules
    while not game.is_winner(1) and not game.is_winner(2):
        move = random.choice(game.legal_moves())
        game.make_move(move, 1)
        if game.is_winner(1):
            return 1
        move = random.choice(game.legal_moves())
        game.make_move(move, 2)
    return 2

def backpropagate(node, result):
    # Backpropagate the result up the tree
    while node is not None:
        node.visits += 1
        node.wins += result
        node = node.parent

def MCTSAgent(game, iterations):
    # Perform MCTS search to find the best move
    root = node()

    for _ in range(iterations):
        node = root
        while not game.is_winner(1) and not game.is_winner(2):
            if node.children == [] or random.random() < 0.5:
                node = expand(node, game)
            else:
                node = select_child(node)
            result = simulate(game)
            backpropagate(node, result)

    best_move = max(root.children, key=lambda x: x.visits).move
    return best_move