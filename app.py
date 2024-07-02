from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from game import Game

app = Flask(__name__)
app.secret_key = 'hi'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
tables_created = False

class UserInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(10), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    game_mode = db.Column(db.String(20), nullable=False)
    player_name = db.Column(db.String(50), nullable=False)

@app.before_request
def create_tables():
    global tables_created
    if not tables_created:
        db.create_all()
        tables_created = True

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
        session.pop('player1', None)
        session.pop('player2', None)
        return redirect(url_for('double_player'))
    elif user_mode == 'Tutorial':
        return redirect(url_for('tutorial'))

@app.route('/double_player', methods=['GET', 'POST'])
def double_player():
    if request.method == 'POST':
        player1 = request.form['player1']
        player2 = request.form['player2']
        
        if not player1 or not player2 or player1 == player2:
            error_message = "Invalid input: Please enter distinct names for both players."
            return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, message=error_message)
        
        session['player1'] = player1
        session['player2'] = player2
        session['first_move_made'] = False

    first_move_made = session.get('first_move_made', False)
    player1 = session.get('player1')
    player2 = session.get('player2')

    return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=first_move_made, player1=player1, player2=player2,message = error_message)

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
    player_name = session.get('player1') if player == 'X' else session.get('player2')

    if not position.isdigit() or int(position) not in range(1, 10) or Game.structure[int(position) - 1] != "_":
        error_message = "Invalid move: Please select a valid position."
        player1 = session.get('player1', 'Player 1')
        player2 = session.get('player2', 'Player 2')
        return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=session['first_move_made'], player1=player1, player2=player2, message=error_message)

    message = Game.update(position, player)

    # Track user input
    user_input = UserInput(player=player, position=int(position), game_mode='Double Player', player_name=player_name)
    db.session.add(user_input)
    db.session.commit()
    
    if not session.get('first_move_made', False):
        session['first_move_made'] = True

    player1 = session.get('player1', 'Player 1')
    player2 = session.get('player2', 'Player 2')

    return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=session['first_move_made'], player1=player1, player2=player2, message=message)

@app.route('/singleplayer_move', methods=['POST'])
def singleplayer_move():
    player = request.form['player']
    position = request.form['position']
    player_name = "Player X" if player == 'X' else "Bot"

    if not position.isdigit() or int(position) not in range(9) or Game.structure[int(position) - 1] != "_":
        error_message = "Invalid move: Please select a valid position."
        return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=session.get('first_move_made', False), error_message=error_message)

    message = Game.update(position, player)

    # Track user input for player
    user_input = UserInput(player=player, position=int(position) - 1, game_mode='Single Player', player_name=player_name)
    db.session.add(user_input)
    db.session.commit()

    if not session.get('first_move_made', False):
        session['first_move_made'] = True

    if Game.current_player == 'O' and not message:
        bot_position, bot_message = Game.bot_move_logic()

        # Track user input for bot
        bot_input = UserInput(player='O', position=bot_position, game_mode='Single Player', player_name="Bot")
        db.session.add(bot_input)
        db.session.commit()

        message = bot_message if bot_message else message

    return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=session['first_move_made'], message=message)

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
    session['first_move_made'] = False
    if source == 'single_player':
        return redirect(url_for('single_player'))
    elif source == 'tutorial':
        return redirect(url_for('tutorial'))
    else:
        return redirect(url_for('double_player'))
    
if __name__ == '__main__':
    app.run(debug=True)
