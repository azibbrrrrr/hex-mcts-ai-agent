AI Agent for Hex
Our AI agent is designed to play the game of Hex using a Monte Carlo Tree Search (MCTS) approach.

Swap Policy
A key aspect of our strategy is the swap policy, which determines whether the agent should swap colors when playing second. The decision is based on predefined board positions, prioritizing central and elongated placements that may give the opponent an advantage. If the opponent’s first move falls into these critical positions, the agent swaps to gain a more favorable board position.

MCTS for Decision-Making
Once the swap decision is made, the agent executes its moves using Monte Carlo Tree Search (MCTS) to find the most promising action. MCTS is a heuristic search algorithm that balances exploration (trying new moves) and exploitation (favoring moves that have led to success in simulations). The agent improves its move selection by running multiple simulations per turn, evaluating different possibilities before making a decision.

Here’s how MCTS works to beat the opponent:

Selection: The algorithm starts at the current game state and selects moves based on a balance of prior success and potential exploration.
Expansion: It expands the game tree by adding a new node when an unexplored move is encountered.
Simulation (Rollout): It simulates a random playout from that position to estimate the likelihood of winning. The game is played out until a winner is determined, using random or heuristic-based moves.
Backpropagation: The results of the simulation are backpropagated up the tree, updating the win/loss statistics for the explored moves.
Move Selection: After running many simulations, the move with the best winning probability is chosen as the agent’s next move.
By repeatedly simulating thousands of games, MCTS refines its decision-making to prioritize moves that lead to victory. This enables the agent to strategically block the opponent, build strong connections, and control key board positions, ultimately improving its chances of winning against human or AI opponents.
