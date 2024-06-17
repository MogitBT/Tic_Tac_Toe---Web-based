import random
import os
import pickle
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

class Game:
    structure = ["_" for _ in range(9)]
    current_player = 'X'  # Track the current player

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
        Game.current_player = 'X'  # Reset the current player to 'X'


@app.route('/')
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
    return render_template('single_player.html', game = Game.layout(), current_player = Game.current_player)

@app.route('/doubleplayer_move', methods=['POST'])
def doubleplayer_move():
    player = request.form['player']
    position = request.form['position']

    valid_move = Game.user_input(position, player)

    if valid_move:
        if Game.check(player):
            message = f'Player {player} won!'
            Game.refresh()
        elif Game.draw():
            message = 'Match Draw!'
            Game.refresh()
        else:
            message = ''
            Game.current_player = 'O' if player == 'X' else 'X'
    else:
        message = 'Invalid move'

    return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, message=message)

@app.route('/singleplayer_move', methods=['POST'])
def singleplayer_move():
    player = request.form['player']
    position = request.form['position']

    valid_move = Game.user_input(position, player)

    if valid_move:
        if Game.check(player):
            message = f'Player {player} won!'
            Game.refresh()
        elif Game.draw():
            message = 'Match Draw!'
            Game.refresh()
        else:
            message = ''
            Game.current_player = 'O' if player == 'X' else 'X'
    else:
        message = 'Invalid move'

    return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player, message=message)

@app.route('/refresh', methods =['POST', 'GET'])
def refresh():
    if request.method == 'POST':
        source = request.form.get('source')
    else:
        source = request.args.get('source')

    if source == 'single_player':
        Game.refresh()
        return redirect(url_for('single_player'))
    else:
        Game.refresh()
        return redirect(url_for('double_player'))
        

if __name__ == '__main__':
    app.run(debug=True)
