"""
Handles game state, valid moves, and AI moves
"""
import numpy as np
import chess

class GameState:
    def __init__(self) -> None:
        # all actual game logic is handled by chess module
        self.board = chess.Board() # initialize starting board
        
        # dict for UI
        self.board_dict = {
            "a8":"r", "b8":"n", "c8":"b", "d8":"q", "e8":"k", "f8":"b", "g8":"n", "h8":"r",
            "a7":"p", "b7":"p", "c7":"p", "d7":"p", "e7":"p", "f7":"p", "g7":"p", "h7":"p",
            "a6":"-", "b6":"-", "c6":"-", "d6":"-", "e6":"-", "f6":"-", "g6":"-", "h6":"-",
            "a5":"-", "b5":"-", "c5":"-", "d5":"-", "e5":"-", "f5":"-", "g5":"-", "h5":"-",
            "a4":"-", "b4":"-", "c4":"-", "d4":"-", "e4":"-", "f4":"-", "g4":"-", "h4":"-",
            "a3":"-", "b3":"-", "c3":"-", "d3":"-", "e3":"-", "f3":"-", "g3":"-", "h3":"-",
            "a2":"P", "b2":"P", "c2":"P", "d2":"P", "e2":"P", "f2":"P", "g2":"P", "h2":"P",
            "a1":"R", "b1":"N", "c1":"B", "d1":"Q", "e1":"K", "f1":"B", "g1":"N", "h1":"R",
        }

    def move_piece_ui(self, move: chess.Move) -> None:
        """gets a UCI from the move input and updates the internal dictionnary for visuals. Need to call before draw_game_state from main."""            
        
        uci = move.uci()
        castling = ["e1g1", "e1c1", "e8g8", "e8c8"]
        piece = self.board_dict[uci[:2]]

        # additional logic for handling castling
        if uci in castling:
            if piece in "Kk":
                # king move
                self.board_dict[uci[:2]] = "-"
                self.board_dict[uci[2:]] = piece
                # rook move
                if uci[2] == "c": # if castling queen side
                    self.board_dict["a"+uci[1]] = "-" # empty the rook square                    
                    # move the correct rook
                    if uci[1] == "1":
                        self.board_dict["d1"] = "R"
                    else:
                        self.board_dict["d8"] = "r"
                else: # castling king side
                    self.board_dict["h"+uci[1]] = "-" # empty the rook square                    
                    # move the correct rook
                    if uci[1] == "1":
                        self.board_dict["f1"] = "R"
                    else:
                        self.board_dict["f8"] = "r"
        # otherwise mark the current square as empty and move the piece to the new square        
        else:
            self.board_dict[uci[:2]] = "-"
            self.board_dict[uci[2:]] = piece


