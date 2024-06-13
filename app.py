import random
import os
import pickle
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

class game:

    structure = ["_" for i in range(9)]
    current_mode = None

    def layout():
        return [game.structure[i:i+3] for i in range(0, 9, 3)]

    def user1_input(position):
        if position.isdigit() and int(position) in range(1, 10):
            if game.structure[int(position) - 1] == "_":
                game.structure[int(position) - 1] = "X"
                return True
            else:
                return False
        return False

    def user2_input(position):
        if position.isdigit() and int(position) in range(1, 10):
            if game.structure[int(position) - 1] == "_":
                game.structure[int(position) - 1] = "O"
                return True
            else:
                return False
        return False

    def check(player):
        combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for possibility in combinations:
            if all(game.structure[i] == player for i in possibility):
                return True
        return False

    def draw():
        return "_" not in game.structure

    def refresh():
        game.structure = ["_" for i in range(9)]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/select_mode', methods = ['POST'])
def user_mode():
    user_mode = request.form.get('mode')
    if user_mode == '1':
        return render_template('single_player.html')
    elif user_mode == '2':
        return redirect(url_for('double_player'))
    else:
        return "Invalid mode selected"

@app.route('/double_player')
def double_player():
    return render_template('double_player.html', game=game.layout(), message='')

@app.route('/move', methods=['POST'])
def move():
    player = request.form['player']
    position = request.form['position']
    
    if player == 'X':
        valid_move = game.user1_input(position)
    elif player == 'O':
        valid_move = game.user2_input(position)
    else:
        valid_move = False
    
    if valid_move:
        if game.check(player):
            message = f'Player {player} won!'
            game.refresh()
        elif game.draw():
            message = 'Match Draw!'
            game.refresh()
        else:
            message = ''
    else:
        message = 'Invalid move'
    
    return render_template('index.html', game=game.layout(), message=message)

@app.route('/refresh')
def refresh():
    game.refresh()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
