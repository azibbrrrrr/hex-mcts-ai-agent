import numpy as np
from copy import deepcopy
from collections import defaultdict
from time import sleep
import sys
import os
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Add the 'src' directory to the sys.path
sys.path.insert(0, src_dir)

from Move import Move
from Colour import Colour

class MonteCarloTreeSearchNode():
    def __init__(self, state, colour, root_colour=None, parent=None, parent_action=None):
        self.state = state
        self.colour = colour  
        if root_colour == None:
            self.root_colour = parent.root_colour
        else:
            self.root_colour = root_colour 

        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_actions = None
        self._untried_actions = self.untried_actions()
        return


    def untried_actions(self):
        self._untried_actions = self.get_legal_actions(self.state, self.colour)
        return self._untried_actions


    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses


    def n(self):
        return self._number_of_visits


    def expand(self):
        action = self._untried_actions.pop()
        next_state = self.move(action,deepcopy(self.state))
        child_node = MonteCarloTreeSearchNode(
            next_state, colour = Colour.opposite(self.colour), parent=self, parent_action=action)
        
        self.children.append(child_node)
        return child_node


    def is_terminal_node(self):
        return self.is_game_over(self.state) 


    def rollout(self):
        current_rollout_state = deepcopy(self.state)
        rollout_colour = self.colour

        while not current_rollout_state.has_ended():
            possible_moves = self.get_legal_actions(current_rollout_state, rollout_colour)
            action = self.rollout_policy(possible_moves)
            current_rollout_state = self.move(action,current_rollout_state)
            rollout_colour = Colour.opposite(rollout_colour)

        return self.game_result(current_rollout_state)


    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)


    def is_fully_expanded(self):
        return len(self._untried_actions) == 0


    def best_child(self, c_param=0.1):
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]


    def rollout_policy(self, possible_moves):
        move = possible_moves[np.random.randint(len(possible_moves))]
        return move


    def _tree_policy(self):
        current_node = self
        
        while not current_node.is_terminal_node():
            
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()

        return current_node


    def best_action(self):
        simulation_no = 500
        
        for i in range(simulation_no):
            # print("SIMULATION NUMBER", i)
            v = self._tree_policy()
            # print("GOT V")
            reward = v.rollout()
            # print("GOT REWARD")
            v.backpropagate(reward)
            # print("DONE PROPOGATING")
        
        return self.best_child(c_param=0.1).parent_action


    def get_legal_actions(self, board, colour): 
        '''
            Constructs a list of all
            possible actions from current state.
            Returns a list.
        '''
        # +i is DOWN
        # +j is RIGHT
        board_string = board.print_board(bnf=True)
        board = board_string.split(',')  # This will give a list of STRINGS
        # Where each string is a row
        moves = []
        
        for i in range(len(board)):
            for j in range(len(board)):
                if (board[i][j] != "R" and board[i][j] != "B"):
                        moves.append(Move(colour, i, j))
        return moves

    def is_game_over(self,state):
        '''
           Returns true or false
        '''
        if state.get_winner() == None:
            return False
        else:
            return True


    def game_result(self,state):
        '''
            Win = 1
            Loss = -1
        '''
        if state.get_winner() == self.root_colour:
            return 1
        elif state.get_winner() == self.opp_colour(self.root_colour):
            return -1
        else:
            return 0 


    def move(self,action,state):
        '''
            Changes the state of your 
            board with a new value.
            python Hex.py "a=Jing;python C:\\Users\\USER\\GitRepos\\COMP34111_v26161ns\\agents\\Group53\\AgentJing.py"
        '''
        
        action.move(state)
        return state 


    def opp_colour(self, colour):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        
        if colour == "R":
            return "B"
        elif colour == "B":
            return "R"
        else:
            return "None"



# if (__name__ == "__main__"):
#     root = MonteCarloTreeSearchNode(state = None)
#     selected_node = root.best_action()
#     return 
