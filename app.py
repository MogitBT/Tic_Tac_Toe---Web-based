from flask import Flask, render_template, request, redirect, url_for
from game import Game

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/select_mode', methods=['POST'])
def user_mode():
    user_mode = request.form.get('mode')
    if user_mode == '1':
        return redirect(url_for('single_player'))
    elif user_mode == '2':
        return redirect(url_for('double_player'))
    elif user_mode == '3':
        return redirect(url_for('tutorial'))

@app.route('/double_player')
def double_player():
    return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player)

@app.route('/single_player')
def single_player():
    return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player)

@app.route('/tutorial')
def tutorial():
    Game.refresh()
    Game.tutorial_logic()
    return render_template('tutorial.html', game=Game.layout(), current_player=Game.current_player)

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
        message = Game.bot_move_logic()

    return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player, message=message)

@app.route('/tutorial_move', methods=['POST'])
def tutorial_move():
    player = request.form['player']
    position = request.form['position']

    message = Game.tutorial_update(position)
    return render_template('tutorial.html', game=Game.layout(), current_player=Game.current_player, message=message)

@app.route('/refresh', methods=['POST'])
def refresh():
    source = request.form.get('source')
    Game.refresh()
    if source == 'single_player':
        return redirect(url_for('single_player'))
    elif source == 'tutorial':
        return redirect(url_for('tutorial'))
    else:
        return redirect(url_for('double_player'))

if __name__ == '__main__':
    app.run(debug=True)
