"""
Main driver file, handles player input and displays game state
"""


# region: imports
import pygame as pg
import chess
import ai
import chessengine
import threading

# endregion

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000 # consider leaving room for move log, but that might not be where I end up displaying that.
FPS = 30
BOARD_SIZE = 1000
SQ_SIZE = BOARD_SIZE/8
IMAGES = {}

# screen
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Chess Game")



def main():
    
    # region: init
    pg.init()
    clock = pg.time.Clock() 
    load_images()

    # variables
    global gs
    global sq_selected
    global player_clicks
    global player_turn
    gs = chessengine.GameState()
    sq_selected = "temp" # string name for square
    player_clicks = [] # store sq_selected
    player_turn = True # Initialize as player's turn

    # endregion


    # game run loop
    run = True
    while run:

        # events
        for event in pg.event.get():
            # handle quit event
            if event.type == pg.QUIT:
                run = False
            # handle mouse click    
            elif event.type == pg.MOUSEBUTTONDOWN:
                if player_turn: # Only handle clicks if it's the player's turn
                    handle_click()
        
        # Check if it's the player's turn and there are no illegal moves
        if player_turn and not gs.board.is_checkmate() and len(player_clicks) == 2:
            make_move(player_clicks) # Make the player's move

        # If it's the AI's turn and the game is not over
        if not player_turn and not gs.board.is_checkmate():
            pg.display.flip() # force update the display before thiking about the move
            draw_game_state()
            ai_move() # Make the AI's move
        
        clock.tick(FPS) # set fixed FPS
        pg.display.flip()
        draw_game_state()


    pg.quit()


def reset_click_log() -> None:
    """cleans the clik log when needed"""
    global sq_selected
    global player_clicks
    sq_selected = ""
    player_clicks = []

def handle_click() -> None:
    """Click event handler. Selects a square that was clicked. If 2 squares were clicked, make a move"""
    global sq_selected
    global player_clicks
    
    location = pg.mouse.get_pos() # (x, y)
    # floor division gets us the nearest int
    col = location[0]//SQ_SIZE # 0 is x
    row = location[1]//SQ_SIZE # 1 is y
    sq_name = get_square_uci(int(col), int(row)) # convert the coord to UCI (i.e. (0,0) to a1)

    # TODO: add highlight
    # if we clicked the same square, deselect and reset variables 
    if sq_selected == sq_name:
        reset_click_log()
    # otherwise store the click
    else:
        sq_selected = sq_name
        player_clicks.append(sq_selected)

def make_move(moves: list) -> None:    
    """Handles move requests. If legal, update UI and game state, then reset click log"""
    global gs
    global player_turn

    if gs.board.is_checkmate() == True: # prevents extra clicks after game over
        return
    
    # concatenate both squares to get UCI move notation
    move = moves[0]+moves[1]
    reset_click_log()
    
    # make the move if its legal
    try:       
        gs.board.push_uci(move) # update board state
        gs.move_piece_ui(chess.Move.from_uci(move)) # update UI dict
        draw_game_state() # draw the updated dict
        player_turn = False
    except chess.IllegalMoveError: # catch illegal moves and notify the player
        print("Illegal move:", move)
 

def ai_move() -> None:
    global gs
    global player_turn

    ai_move = ai.ai_move(gs.board) # get a AI move
    gs.board.push(ai_move) # update board state
    gs.move_piece_ui(ai_move) # update UI dict
    draw_game_state() # draw the updated dict 
    player_turn = True

# Converts a click coordinate to UCI
def get_square_uci(col: int, row: int) -> str:
    # check if we got a valid input
    if not 0 <= col <= 7 or not 0 <= row <= 7:
        raise ValueError("Invalid square clicked")

    # Convert column index to corresponding ASCII character
    col_char = chr(ord('a') + col)
    return f"{col_char}{(7 - row + 1)}" # need to invert the row number

# draws all graphics elements of the current game state
def draw_game_state() -> None:
    screen.blit(choose_board(), (0,0)) # Draw the chessboard image
    draw_pieces()


def draw_pieces() -> None:
    global gs
    for square, piece in gs.board_dict.items():
        if piece != "-":  # if it's not an empty space
            # Convert square notation to coordinates
            col = ord(square[0]) - ord('a')
            row = 8 - int(square[1])
            screen.blit(IMAGES[piece], pg.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))




# loads the images on init and set the global images dictionnary
def load_images() -> None:
    pieces = ["R", "N", "B", "Q", "K", "P", "br", "bn", "bb", "bq", "bk", "bp"]

    # file names are case insensitive, so using this [:-1] trick to keep consistency with the backend notation
    for piece in pieces:
        IMAGES[piece[-1]] = pg.transform.scale(pg.image.load("../assets/pieces/"f"{piece}.png"), (SQ_SIZE, SQ_SIZE))

# display new image
def draw_sprite(obj, position):
    screen.blit(obj, position)
    pg.display.update()

# WIP: lets the player choose a board. Defaults to green
def choose_board(board_chosen="board_green") -> pg.image:

    board_img = pg.image.load("../assets/boards/"f"{board_chosen}.png")
    board_img = pg.transform.scale(board_img, (BOARD_SIZE, BOARD_SIZE))
    return board_img


if __name__ == "__main__":
    main()