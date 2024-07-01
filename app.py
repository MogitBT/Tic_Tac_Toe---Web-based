from flask import Flask, render_template, request, redirect, url_for, session
from game import Game

app = Flask(__name__)
app.secret_key = 'hi'

@app.route('/', methods=['GET', 'POST'])
def home():
    Game.structure = ["_" for _ in range(9)]
    return render_template('home.html', game=Game.layout())

@app.route('/select_mode', methods=['POST'])
def user_mode():
    user_mode = request.form.get('mode')
    if user_mode == 'Single Player':
        return redirect(url_for('single_player'))
    elif user_mode == 'Double Player':
        session['first_move_made'] = False
        return redirect(url_for('double_player'))
    elif user_mode == 'Tutorial':
        return redirect(url_for('tutorial'))

@app.route('/double_player')
def double_player():
    first_move_made = session.get('first_move_made', False)
    return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=first_move_made)

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
    
    if not session.get('first_move_made', False):
        session['first_move_made'] = True

    return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=session['first_move_made'], message=message)

@app.route('/singleplayer_move', methods=['POST'])
def singleplayer_move():
    player = request.form['player']
    position = request.form['position']

    message = Game.update(position, player)

    if not session.get('first_move_made',False):
        session['first_move_made'] = True

    if Game.current_player == 'O' and not message:
        message = Game.bot_move_logic()

    return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player,first_move_made=session['first_move_made'], message=message)

@app.route('/tutorial_move', methods=['POST'])
def tutorial_move():
    player = request.form['player']
    position = request.form['position']

    if not session.get('first_move_made',False):
        session['first_move_made'] = True

    message = Game.tutorial_update(position)
    return render_template('tutorial.html', game=Game.layout(), current_player=Game.current_player, first_move_made=session['first_move_made'], message=message)

@app.route('/refresh', methods=['POST'])
def refresh():
    source = request.form.get('source')
    Game.refresh()
    session['first_move_made'] = False
    if source == 'single_player':
        return redirect(url_for('single_player'))
    elif source == 'tutorial':
        return redirect(url_for('tutorial'))
    else:
        return redirect(url_for('double_player'))

if __name__ == '__main__':
    app.run(debug=True)
