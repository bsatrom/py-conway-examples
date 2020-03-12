import sys
import time
import os

from PyInquirer import prompt, print_json, Validator, ValidationError
from clint.arguments import Args

from py_conway import Game, GameState
from pprint import pprint
from pyfiglet import Figlet

figlet = Figlet(font='slant')

args = Args()
questions = list()
parsed_args = dict()


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))


if len(args) > 0:
    for arg_index in range(0, len(args), 2):
        if (args[arg_index] == '-w' or args[arg_index] == '--width'):
            parsed_args.update({'board_width': args[arg_index+1]})
        elif (args[arg_index] == '-h' or args[arg_index] == '--height'):
            parsed_args.update({'board_height': args[arg_index+1]})
        elif (args[arg_index] == '-i' or args[arg_index] == '--infinite'):
            parsed_args.update({'enforce_boundary': args[arg_index+1]})

if 'board_height' not in parsed_args:
    questions.append({
        'type': 'input',
        'name': 'board_height',
        'message': 'How high should the board be?',
        'default': '12',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    })

if 'board_width' not in parsed_args:
    questions.append({
        'type': 'input',
        'name': 'board_width',
        'message': 'How wide should the board be?',
        'default': '12',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    })

if 'enforce_boundary' not in parsed_args:
    questions.append({
        'type': 'confirm',
        'name': 'enforce_boundary',
        'message': 'Run in infinite mode?',
        'default': True
    })

print(figlet.renderText('Py-Conway!'))

if len(questions) > 0:
    print(f"Received {3 - len(questions)} of 3 arguments...")
    answers = prompt(questions)

    for answer_key in answers.keys():
        parsed_args.update({ answer_key: answers[answer_key]})

pprint(parsed_args)

print("Received all arguments. Starting game...")

conway_game = Game(
    columns = int(parsed_args.get('board_width')),
    rows = int(parsed_args.get('board_height')),
    enforce_boundary= bool(parsed_args.get('enforce_boundary')),
    random = True
)
conway_game.start()

# Linux/macOS Clear Command
clear_cmd = "clear"
# Change for Windows
if os.name =="nt": 
    clear_cmd = "cls"

def replace_cell(index, current_item, row):
    return_val = "🐍" if current_item == 1 else " "
    if (index+1 == len(row)):
        return_val += "\n"

    return return_val

while conway_game.live_cells > 0:
    os.system(clear_cmd)
    sys.stdout.write(
        f'🐍 Living Cells: {conway_game.live_cells} | Generation: {conway_game.generations} 🐍\n\n'
    )
    
    game_board = [replace_cell(index, item, row) 
                  for row in conway_game.current_board
                  for index, item in enumerate(row)]
    
    sys.stdout.write(''.join(game_board))
    sys.stdout.flush()
    
    time.sleep(.15)

    conway_game.run_generation()

print("Game finished!")