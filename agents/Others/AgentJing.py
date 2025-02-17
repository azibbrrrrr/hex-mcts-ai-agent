import socket
from random import choice
from time import sleep
import sys
import os
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Add the 'src' directory to the sys.path
sys.path.insert(0, src_dir)

from MCTSAgent import MonteCarloTreeSearchNode
from Board import Board
from Colour import Colour
from Move import Move
from copy import deepcopy

class NaiveAgent():
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """
        
        self._board_size = 0
        self._board = []
        self._colour = ""
        self._turn_count = 1
        self._choices = []
        
        states = {
            1: NaiveAgent._connect,
            2: NaiveAgent._wait_start,
            3: NaiveAgent._make_move,
            4: NaiveAgent._wait_message,
            5: NaiveAgent._close
        }

        res = states[1](self)
        while (res != 0):
            res = states[res](self)

    def _connect(self):
        """Connects to the socket and jumps to waiting for the start
        message.
        """
        
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((NaiveAgent.HOST, NaiveAgent.PORT))

        return 2

    def _wait_start(self):
        """Initialises itself when receiving the start message, then
        answers if it is Red or waits if it is Blue.
        """
        
        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "START"):
            self._board_size = int(data[1])
            for i in range(self._board_size):
                for j in range(self._board_size):
                    self._choices.append((i, j))
            self._colour = data[2]

            self._board = Board(self._board_size)

            # TEST _____________________________________________________________________________

            # root = MonteCarloTreeSearchNode(state = self._board, colour = self._colour, root_colour = self._colour)
            # test_state = deepcopy(root.state)
            # test_move = Move(Colour.RED,0,0)
            # root.move(test_move, test_state)
            # # print(root.get_legal_actions(self._board))
            # # self._board.set_tile_colour(0,0,'R')
            # print(root.state.print_board(False))

            #_______________________________________________________________________________
            if (self._colour == "R"):
                return 3
            else:
                return 4

        else:
            print("ERROR: No START message received.")
            return 0

    def _make_move(self):
        """Makes a random valid move. It will choose to swap with
        a coinflip.
        """
        # self._board.print_board()
        if (self._turn_count == 2 and choice([0, 1]) == 1):
            pass
        else:
            if self._colour == "R":
                root_colour = Colour.RED
            elif self._colour == "B":
                root_colour = Colour.BLUE
            else:
                root_colour = None
            # print("BOARD STATE")
            # print(self._board.print_board(False))
            root = MonteCarloTreeSearchNode(state = self._board, colour = root_colour, root_colour = root_colour)            
            selected_node = root.best_action()
            
            msg = f"{selected_node.x},{selected_node.y}\n"
            selected_node.move(self._board)
            # print("BOARD STATE AFTER MOVE")
            # print(self._board.print_board(False))
        
        self._s.sendall(bytes(msg, "utf-8"))
        

        return 4

    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "END" or data[-1] == "END"):
            return 5
        else:

            if (data[1] == "SWAP"):
                self._colour = self.opp_colour()
            else:
                x, y = data[1].split(",")
                self._choices.remove((int(x), int(y)))

            if (data[-1] == self._colour):
                try:
                    x, y = data[1].split(",")
                    
                    if self._colour == 'R':
                        eneum_colour_form = Colour.RED
                    elif self._colour == 'B':
                        eneum_colour_form = Colour.BLUE
                    else:
                        eneum_colour_form = None
                    opp_move = Move(Colour.opposite(eneum_colour_form),int(x),int(y))
                    opp_move.move(self._board)
                    print("BOARD STATE AFTER OPP MOVE")
                    print(self._board.print_board(False))
                    
                except ValueError:
                    pass
                
                return 3

        return 4

    def _close(self):
        """Closes the socket."""

        self._s.close()
        return 0

    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        
        if self._colour == "R":
            return "B"
        elif self._colour == "B":
            return "R"
        else:
            return "None"


if (__name__ == "__main__"):
    agent = NaiveAgent()
    agent.run()
