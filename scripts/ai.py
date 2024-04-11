import keras
import numpy as np
import chess

"""
This script is responsible for generating AI moves.
It takes in a FEN notation and returns a UCI notation move decided by the AI.
"""

# load model when file is imported
model = keras.models.load_model("./local/first_model_keep_training.keras")

def fen2bitboard(fen: str, to_bits: bool=False) -> np.array:
    """
    Returns bitboard [np 1D array(773)] from fen. Can return bits is to_bits=True
    """
    # each square is assigned 12 bits to represent each piece, that's what the mapping is for
    mapping = {
                "p": 0,
                "n": 1,
                "b": 2,
                "r": 3,
                "q": 4,
                "k": 5,
                "P": 6,
                "N": 7,
                "B": 8,
                "R": 9,
                "Q": 10,
                "K": 11
                }
    
    # initialize the array with zeros
    bitboard = np.zeros(773, dtype=int)
    currIndex = 0
    
    try:
        position, turn, castling, _, _, _ = fen.split(" ") # keep only useful data
    except:
        position, turn, castling, _ = fen.split(" ")
    
    for ch in position:
        if ch == "/": # "/" represent rows, simply ignore that
            continue
        elif ch.isdigit(): # a digit means an empty space, skip ahead that many indexes
            currIndex += int(ch) * 12 # multiply by 12 because there are 12 bits used for each square
        else:
            bitboard[currIndex + mapping[ch]] = 1 # set the correct bit to 1
            currIndex += 12 # get to next bit
    
    # add details about the game state
    bitboard[768] = 1 if turn == "w" else 0
    bitboard[769] = 1 if "K" in castling else 0
    bitboard[770] = 1 if "Q" in castling else 0
    bitboard[771] = 1 if "k" in castling else 0
    bitboard[772] = 1 if "q" in castling else 0
    
    if to_bits:
        return np.packbits(bitboard)
    return bitboard

def get_eval(board: chess.Board) -> float:
    """Takes in a board, gets the bitboard from it, reshape the array, feed it to the model and returns an evaluation"""  
    
    bitboard = fen2bitboard(board.fen())
    pos = np.reshape(bitboard, (1, 773)) # model expects a dimension for the batch size   
    return model.predict(pos)[0][0]


def ai_move(board: chess.Board) -> chess.Move:
    """Takes a chess board and returns the best move. It picks the top 5 moves, goes down each line and choses the moves that leads to the best position."""

    turn = board.turn #store the turn

    all_eval = []
    all_moves = []
    # looks at all the legal moves in a given position (legal_moves returns UCI)
    for move in board.legal_moves:
        all_moves.append(move) # store the move
        temp_board = board.copy() # make a temp copy of the board
        temp_board.push(move) # make the move on the temporary board
        pred = get_eval(temp_board) # evaluate the position
        all_eval.append(pred) # store the eval at the same index as the move

    if turn: # returns true if it's white's turn -> get the 5 highest eval
        ind = np.argpartition(all_eval, -5)[-5:]
    else:  # if it's black, get the 5 lowest
        ind = np.argpartition(all_eval, 5)[:5]

    candidate_moves = [all_moves[i] for i in ind]
    candidate_eval = []
    
    for move in candidate_moves:
        temp_board = board.copy() # make a temp copy of the board
        temp_board.push(move) # make the move on the temporary board
        candidate_eval.append(explore_move(temp_board, 5)) # go down the lines and see what's the eval
    
    if turn:
        best = np.argmax(candidate_eval)
    else:
        best = np.argmin(candidate_eval)

    return candidate_moves[best]



def explore_move(board: chess.Board, depth=4) -> float:
    """Takes in a board states and makes the best move for each sides until depth is reached.
    Returns a float for the resulting position's eval."""


    local_board = board.copy() # copy the board to avoid making changes top the real

    for _ in range(depth):
        all_eval = []
        all_moves = []
        turn = local_board.turn

        # looks at all the legal moves in a given position
        for move in local_board.legal_moves:
            all_moves.append(move) # store the move
            temp_board = local_board.copy() # make a temp copy of the board
            temp_board.push(move) # make the move on the temporary board
            pred = get_eval(temp_board) # evaluate the position
            all_eval.append(pred) # store the eval at the same index as the move

        if turn: # returns true if it's white's turn -> get the 5 highest eval
            ind = np.argmax(all_eval)
        else:  # if it's black, get the 5 lowest
            ind = np.argmin(all_eval)

        local_board.push(all_moves[ind]) # push the chosen move to the board

    # return the eval of the final position
    return get_eval(local_board)