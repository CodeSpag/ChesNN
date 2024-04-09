import keras
import numpy as np
import chess

"""
This script is responsible for generating AI moves.
It takes in a FEN notation and returns a UCI notation move decided by the AI.
"""

# load model when file is imported
model = keras.models.load_model("first_model_keep_training.keras")

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

def get_eval(bitboard: np.array) -> float:
    """reshape the array, feed it to the model and returns an evaluation"""  
    
    pos = np.reshape(bitboard, (1, 773)) # model expects a dimension for the batch size   
    return model.predict(pos)[0][0]


def ai_move(fen: str) -> str:
    """Takes a FEN notation board and returns a move in UCI notation.
    For now it only looks at 1 position."""

    board = chess.Board(fen) # create a board for the chess library
    bitboard = fen2bitboard(fen)
    turn = bitboard[768] # where the turn is stored
    

    all_eval = []
    all_moves = []
    # looks at all the legal moves in a given position
    for move in board.legal_moves:
        all_moves.append(move) # store the move
        temp_board = board.copy() # make a temp copy of the board
        temp_board.push(move) # make the move on the temporary board
        pred = get_eval(fen2bitboard(temp_board.fen())) # evaluate the position
        all_eval.append(pred) # store the eval at the same index as the move

    if turn == 1: #it's white's turn, get the highest eval
        idx = np.argmax(all_eval)
        print("ai eval for white:", all_eval[idx])
    else:  # if it's black, get the lowest
        idx = np.argmin(all_eval)
        print("ai eval for black:", all_eval[idx])

    out = all_moves[idx]

    return out.uci()