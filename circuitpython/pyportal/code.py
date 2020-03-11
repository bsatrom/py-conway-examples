import displayio
import board
import terminalio
import adafruit_imageload
import adafruit_touchscreen

from time import sleep
from adafruit_display_text import label
import neopixel

from py_conway.game import Game, GameState

"""Game Variables"""
# Large board
#pixel_size = 16
#board_width = 9
#board_height = 7

# Small board option
pixel_size = 16
board_width = 19
board_height = 14

game_width = board_width * pixel_size
game_height = board_height * pixel_size

DEFAULT_PIXEL = 2  # Use 4 For MHO
LIVE_PIXEL = 0

is_game_running = False
is_game_over = False

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

touchscreen = adafruit_touchscreen.Touchscreen(
                            board.TOUCH_XL, board.TOUCH_XR,
                            board.TOUCH_YD, board.TOUCH_YU)

# neopixel colors
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

display = board.DISPLAY

screen_width = display.width
screen_height = display.height

# Remove enforce_boundary to respect the outer edges of the board
cpy_game = Game(board_height, board_width, random=True, enforce_boundary=False)

# Main Game Groups
splash = displayio.Group()
board_group = displayio.Group()

"""Game Functions"""


def perform_startup():
    # Make the display context
    display.show(splash)

    color_bitmap = displayio.Bitmap(screen_width, screen_height, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0xFF00FF  # Purple

    bg_sprite = displayio.TileGrid(color_bitmap,
                                   pixel_shader=color_palette,
                                   x=0, y=0)
    splash.append(bg_sprite)

    # Draw a smaller inner rectangle
    inner_bitmap = displayio.Bitmap(screen_width - 20, screen_height - 20, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0x000000  # Black
    inner_sprite = displayio.TileGrid(inner_bitmap,
                                      pixel_shader=inner_palette,
                                      x=10, y=10)
    splash.append(inner_sprite)

    # Draw a label
    text_group = displayio.Group(max_size=10, scale=4, x=60, y=110)
    text = "PyConway!"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFF00FF)
    text_group.append(text_area)  # Subgroup for text scaling
    splash.append(text_group)

    sleep(1)

    # Remove the text layer to prepare the game
    splash.pop()

    # Draw a label
    text_group = displayio.Group(max_size=10, scale=4, x=55, y=110)
    text = "Touch Me!"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFF00FF)
    text_group.append(text_area)  # Subgroup for text scaling
    splash.append(text_group)


def game_over(num_generations, screen_text="Game Over!", screen_x=47):
    game_over_group = displayio.Group()
    
    over_text_group = displayio.Group(max_size=10, scale=4, x=screen_x, y=100)
    over_text = screen_text = screen_text
    text_area = label.Label(terminalio.FONT, text=over_text, color=0xFF00FF)
    over_text_group.append(text_area)
    game_over_group.append(over_text_group)
    
    generations_group = displayio.Group(max_size=10, scale=2, x=67, y=130)
    gen_text = "Generations: " + str(num_generations)
    gen_text_area = label.Label(terminalio.FONT, text=gen_text, color=0xFF00FF)
    generations_group.append(gen_text_area)
    
    game_over_group.append(generations_group)
    
    pixels.fill(RED)
    pixels.show()
    
    display.show(game_over_group)


def update_board():
    board_state = cpy_game.current_board
    for row in range(len(board_state)):
        for col in range(len(board_state[row])):
            cell_val = LIVE_PIXEL if board_state[row][col] == 1 \
                                  else DEFAULT_PIXEL
            game_board[row, col] = cell_val


def start_game():
    pixels.fill(0x000000)
    pixels.show()

    display.show(board_group)

    cpy_game.reseed()
    cpy_game.start()

    update_board()

"""Game Logic"""
perform_startup()

# Load game sprites. Use the _16pixel file if drawing a larger board
sprite_sheet, palette = adafruit_imageload.load("/cp_sprite_sheet_black_16pixel.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)

game_board = displayio.TileGrid(sprite_sheet,
                                pixel_shader=palette,
                                width=board_width,
                                height=board_height,
                                tile_width=pixel_size,
                                tile_height=pixel_size,
                                default_tile=DEFAULT_PIXEL,
                                x=10,
                                y=10)

board_group.append(game_board)

"""Game Loop"""
while True:
    if not is_game_running:
        if touchscreen.touch_point:
            is_game_running = True
            is_game_over = False

            start_game()
    elif not is_game_over:
        # Add logic here to cancel or stop game
        if touchscreen.touch_point:
            is_game_running = False
            cpy_game.stop()
            game_over(cpy_game.generations)
            is_game_over = True
            continue
            
        # Run the next generation
        if cpy_game.live_cells > 0:
            cpy_game.run_generation()

            if cpy_game.state == GameState.STASIS:
                game_over(cpy_game.generations, screen_text="Stasis!", screen_x=80)
                sleep(4)

                is_game_running = True
                is_game_over = False

                start_game()
            else:
                update_board()
        else:
            is_game_running = False
            cpy_game.stop()
            game_over(cpy_game.generations)
            is_game_over = True
