import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

class Game:
    structure = ["_" for _ in range(9)]
    current_player = 'X'

    @staticmethod
    def layout():
        return [Game.structure[i:i+3] for i in range(0, 9, 3)]

    @staticmethod
    def user_input(position, player):
        if position.isdigit() and int(position) in range(1, 10):
            if Game.structure[int(position) - 1] == "_":
                Game.structure[int(position) - 1] = player
                return True
            else:
                return False
        return False

    @staticmethod
    def check(player):
        combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for possibility in combinations:
            if all(Game.structure[i] == player for i in possibility):
                return True
        return False

    @staticmethod
    def draw():
        return "_" not in Game.structure

    @staticmethod
    def refresh():
        Game.structure = ["_" for _ in range(9)]
        Game.current_player = 'X'  

    @staticmethod
    def update(position, player):
        if Game.user_input(position, player):
            if Game.check(player):
                Game.refresh()
                return f'Player {player} won!'
            elif Game.draw():
                Game.refresh()
                return 'Match Draw!'
            else:
                Game.current_player = 'O' if player == 'X' else 'X'
                return ''
        else:
            return 'Invalid move'


@app.route('/', methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/select_mode', methods=['POST'])
def user_mode():
    user_mode = request.form.get('mode')
    if user_mode == '1':
        return redirect(url_for('single_player'))
    elif user_mode == '2':
        return redirect(url_for('double_player'))
    else:
        return "Invalid mode selected"

@app.route('/double_player')
def double_player():
    return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player)

@app.route('/single_player')
def single_player():
    return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player)

@app.route('/doubleplayer_move', methods=['POST'])
def doubleplayer_move():
    player = request.form['player']
    position = request.form['position']

    message = Game.update(position, player)

    return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, message=message)

@app.route('/singleplayer_move', methods=['POST'])
def singleplayer_move():
    player = request.form['player']
    position = request.form['position']

    message = Game.update(position, player)

    if Game.current_player == 'O' and not message:
        message = bot_move_logic()

    return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player, message=message)

def bot_move_logic():
    player = 'O'
    combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    position = -1

    # Check for winning move
    for combination in combinations:
        bot_count = 0
        empty_spot = -1
        for i in combination:
            if Game.structure[i] == 'O':
                bot_count += 1
            elif Game.structure[i] == '_':
                empty_spot = i
        if bot_count == 2 and empty_spot != -1:
            position = empty_spot
            break

    # Block opponent's winning move
    if position == -1:
        for combination in combinations:
            player_count = 0
            empty_spot = -1
            for i in combination:
                if Game.structure[i] == 'X':
                    player_count += 1
                elif Game.structure[i] == '_':
                    empty_spot = i
            if player_count == 2 and empty_spot != -1:
                position = empty_spot
                break

    # Take the center spot if available
    if position == -1 and Game.structure[4] == '_':
        position = 4

    # Take any available spot
    if position == -1:
        empty_positions = [i for i in range(9) if Game.structure[i] == '_']
        if empty_positions:
            position = random.choice(empty_positions)

    position = str(position + 1)
    message = Game.update(position, 'O')

    return message

@app.route('/refresh', methods=['POST'])
def refresh():
    source = request.form.get('source')
    Game.refresh()
    if source == 'single_player':
        return redirect(url_for('single_player'))
    else:
        return redirect(url_for('double_player'))


if __name__ == '__main__':
    app.run(debug=True)
