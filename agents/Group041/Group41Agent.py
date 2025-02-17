import socket
from MCTSAgent import MCTS
import socket
from random import choice
from time import sleep
import sys
import os

# Get the directory of the current file
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Add the 'src' directory to the sys.path
sys.path.insert(0, src_dir)

class NaiveAgent():
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def non_empty_tiles(self):
        coords = []
        for i in range(11):
            for j in range(11):
                if self._board[i][j] == "R" or self._board[i][j] == "B":
                    coords.append([i,j])

        return coords

    def swap_policy(self):
        central= [[5, 5], [4, 6], [4, 5], [5, 4], [6, 4], [6, 5], [5, 6], [4, 4], [6, 6]] #coords for central swap policy
        elongated_vert= [[5, 5], [6, 5], [7, 5], [4, 5], [3, 5], [7, 6], [6, 6], [5, 6], [4, 6], [3, 6], [3, 4], [4, 4], [5, 4], [6, 4], [7, 4]] #coords for B horizontal elongated swap policy
        elongated_hori=[[5, 5], [6, 5], [4, 5], [6, 6], [5, 6], [4, 6], [4, 4], [5, 4], [6, 4], [6, 3], [5, 3], [4, 3], [6, 7], [5, 7], [4, 7]] #coords for B vertical elongated swap policy

        opp_move_list= self.non_empty_tiles()
        if len(opp_move_list)!=1:
            print("ERROR")

        if opp_move_list[0] in central:
            return True #swap now
        else: 
            return False #dont swap
        
    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """
        
        self._board_size = 0
        self._board = ""
        self._colour = ""
        self._turn_count = 1
        
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
            self._colour = data[2]   #player to start the game
            self._board = [[0] * self._board_size for _ in range(self._board_size)]

            if (self._colour == "R"):
                return 3 # make first move
            else:
                return 4  # wait for next message

        else:
            print("ERROR: No START message received.")
            return 0

    def _make_move(self):
        """Makes a random valid move. It will choose to swap with
        a coinflip.
        """
        if (self._turn_count == 2 and self.swap_policy()==True):
            # If it's the second turn, run the swap policy
            msg = "SWAP\n"
                
        else: 
        # initialise mcts and get best child to make a move
            # print(f"Board before mcts: {self._board}")
            mcts = MCTS(self._colour)
            move = mcts.run_mcts(self._board, time_limit=1)
            self._board[move[0]][move[1]] = self._colour
            # print(f"Board after mcts: {self._board}")
            msg = f"{move[0]},{move[1]}\n"
            print(f"Move made: {msg}")
        self._s.sendall(bytes(msg, "utf-8"))

        return 4

    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1
        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        # Pass board state to Board class
        # self.moveGen(data, 3,3)
        if (data[0] == "END" or data[-1] == "END"):
            return 5
        else:  #data[0] == "CHANGE"
            if (data[1] == "SWAP"):
                self._colour = self.opp_colour()
            else:
                # opponent make move, append change on board
                move = [int(x) for x in data[1].split(",")]

                # Determine the color of the player who made the last move
                if data[-1] == self._colour:
                    self._board[move[0]][move[1]] = self.opp_colour()
                # Update the board when receive changes in board
            if (data[-1] == self._colour):
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
