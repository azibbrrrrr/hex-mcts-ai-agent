import socket
from random import choice
from time import sleep
from src.Colour import Colour
import math

neighbours = [lambda i,j, mult: (i - (1*mult), j), #Abovei
              lambda i,j, mult: (i + (1*mult), j), #Bellow
              lambda i,j, mult: (i, j + (1*mult)),#Right
              lambda i,j, mult: (i, j - (1*mult)),#Left
              lambda i,j, mult: (i - (1*mult), j + (1*mult)),#Diagonal up
              lambda i,j, mult: (i + (1*mult), j - (1*mult))#Diagonal down
              ]#i and j are chords,
               #mult = 1 for neighbours, mult = 2 for neighbours + 1

class NaiveAgent():
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234
    pre_positions = {}
    
    def hasNeighbours(self, board, index):
        connected = 0

        for transform in neighbours:
            neighbourIndex = transform(index[0], index[1], 1)

            #A tile connects if...
            connected += (
                board._tiles[index[0]][index[1]].colour  == #They are the same colour and...
                board._tiles[neighbourIndex[0]][neighbourIndex[1]].colour and
                not board._tiles[neighbourIndex[0]][neighbourIndex[1]].is_visited()#That tile has not been visited
            )

        return connected


    def hasWeakNeighbours(self, board, index):
        connected = 0

        for transform in neighbours:
            neighbourIndex = transform(index[0], index[1], 1)

            nextNeighbourIndex = transform(index[0], index[1], 2)

            if(    (neighbourIndex[0] <= 0 and neighbourIndex[0] >= board._board_size) and

                   (neighbourIndex[1] <= 0 and neighbourIndex[1] >= board._board_size) and

                   (nextNeighbourIndex[0] <= 0 and nextNeighbourIndex[0] >= board._board_size) and
                   
                   (nextNeighbourIndex[1] <= 0 and nextNeighbourIndex[1] >= board._board_size)):
                
                connected += (#A tile is connected if...
                    (
                        board._tiles[index[0]][index[1]].colour  == #The two tiles are the same colour
                        board._tiles[nextNeighbourIndex[0]][nextNeighbourIndex[1]].colour and
                        not board._tiles[nextNeighbourIndex[0]][nextNeighbourIndex[1]].is_visited()#That tile has not been visited
                    )
                    and 
                    (#There is a blank space between the two tiles 
                        board._tiles[neighbourIndex[0]][neighbourIndex[1]].colour ==
                        None
                    )
                )

        return connected

    def evalFunc(self, board):
        # Connected peices - Oponents Connected peices + BlockOponent

        if(board in self.pre_positions.keys()):#for if we impliment a hash table
            return self.pre_positions[board]

        connectedNeighbours, seperatedNeighbours = {Colour.RED: 0, Colour.BLUE: 0}
        Distribution = {Colour.RED: [0,0], #Top, Bottom
                        Colour.BLUE: [0,0]}#Left, Right

        for i in range(board._board_size):

            for j in range(board._board_size):

                tile = board._tiles[i][j]

                if(tile.colour != None):

                    connectedNeighbours[tile.colour] += self.hasNeighbours(board, (i,j))
                    seperatedNeighbours[tile.colour] += self.hasWeakNeighbours(board, (i,j))

                    if(tile.colour == Colour.RED):
                        Distribution[tile.colour][(
                            i >= math.floor(board._board_size/2)
                        )] += 1
                    else:
                        Distribution[tile.colour][(
                            j >= math.floor(board._board_size/2)
                        )] += 1

                tile.visit()

        pass

    
    def moveGen(self, data, iMiddle, jMiddle):
        #+i is DOWN
        #+j is RIGHT

        board = data[2].split(',') #This will give a list of STRINGS
                                   #Where each string is a row
        moves, innerMoves = []

        middleIndex = (len(board)//2) + (len(board)%2) - 1

        jRange = [
            middleIndex - (jMiddle//2
                           + (1 * (0 and jMiddle%2))),#If jMiddle is an even number it needs to offset the middle of the board by one
            middleIndex + (jMiddle//2)
        ]

        iRange = [
            middleIndex - (iMiddle//2
                           + (1 * (0 and iMiddle%2))),#If iMiddle is an even number it needs to offset the middle of the board by one
            middleIndex + (iMiddle//2)
        
        ]                                            
        for i in len(board):

            for j in len(board):

                if (board[i][j] != "R" 
                    and board[i][j] != "B"):

                    if(i >= iRange[0] and i <= iRange[1]
                       and j >= jRange[0] and j <= jRange[1]):
                        innerMoves.append((i,j))
                    else:
                        moves.append((i,j))

        self._choices = innerMoves + moves #Two "returns" depending on how we want to access moves

        return innerMoves + moves


    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """
        
        self._board_size = 0
        self._board = []
        self._colour = ""
        self._turn_count = 1
        self._choices = []  #list to store all possible moves for agent to make
        
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
                    self._choices.append((i, j))  # Initialize _choices with all possible moves
            self._colour = data[2]   #player to start the game

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
        
        #AZ - IMPLEMENT SWAP POLICY HERE
        if (self._turn_count == 2 and choice([0, 1]) == 1): 
            # If it's the second turn and the random choice is 1, perform a swap move
            msg = "SWAP\n"
        else: 
            move = choice(self._choices) # Choose a random move from _choices
            msg = f"{move[0]},{move[1]}\n"
        
        self._s.sendall(bytes(msg, "utf-8"))

        return 4

    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        self.moveGen(data, 3,3)
        if (data[0] == "END" or data[-1] == "END"):
            return 5
        else:  #data[0] == "CHANGE"

            if (data[1] == "SWAP"):
                self._colour = self.opp_colour()
            else:
                x, y = data[1].split(",")
                self._choices.remove((int(x), int(y)))  # Remove the chosen move from _choices bcos it is occupied

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
