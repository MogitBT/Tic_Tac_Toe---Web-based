from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from game import Game

app = Flask(__name__)
app.secret_key = 'hi'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
tables_created = False

class UserInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(36), nullable=False)
    player = db.Column(db.String(10), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    game_mode = db.Column(db.String(20), nullable=False)
    player_name = db.Column(db.String(50), nullable=False)
    win_status = db.Column(db.String(50), nullable=True)

@app.before_request
def create_tables():
    global tables_created
    if not tables_created:
        db.create_all()
        tables_created = True

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'game_id' not in session:
        session['game_id'] = str(uuid.uuid4().hex[4])

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
            game_id = session.get('game_id')
            move_log = UserInput.query.filter_by(game_id=game_id, game_mode='Double Player').all()
            return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, error_message=error_message, move_log=move_log)
        
        session['player1'] = player1
        session['player2'] = player2
        session['first_move_made'] = False
        session['game_id'] = str(uuid.uuid4())

    first_move_made = session.get('first_move_made', False)
    player1 = session.get('player1')
    player2 = session.get('player2')
    game_id = session.get('game_id')
    move_log = UserInput.query.filter_by(game_id=game_id, game_mode='Double Player').all()

    return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=first_move_made, player1=player1, player2=player2, move_log=move_log)

@app.route('/doubleplayer_move', methods=['POST'])
def doubleplayer_move():
    player = request.form['player']
    position = request.form['position']
    game_id = session.get('game_id')

    if not game_id:
        session['game_id'] = str(uuid.uuid4())
        game_id = session['game_id']

    player1 = session.get('player1', 'Player 1')
    player2 = session.get('player2', 'Player 2')

    if not position.isdigit() or int(position) not in range(1, 10) or Game.structure[int(position) - 1] != "_":
        error_message = "Invalid move: Please select a valid position."
        move_log = UserInput.query.filter_by(game_id=game_id, game_mode='Double Player').all()
        return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=session.get('first_move_made', False), message=error_message, player1=player1, player2=player2, move_log=move_log)

    message = Game.update(position, player)
    win_status = None
    game_end = 0

    if "Player X won" in message:
        win_status = f'{player1} Won'
        session['game_id'] = str(uuid.uuid4())
        game_end =1
    elif "Player O won" in message:
        win_status = f'{player2} Won'
        session['game_id'] = str(uuid.uuid4())
        game_end = 1
    elif "Match Draw!" in message:
        win_status = "Draw"
        session['game_id'] = str(uuid.uuid4())
        game_end = 1
    else:
        game_end = 0

    if not session.get('first_move_made', False):
        session['first_move_made'] = True

    player_name = session.get('player1') if player == 'X' else session.get('player2')
    user_input = UserInput(game_id=game_id, player=player, position=int(position) - 1, game_mode='Double Player', player_name=player_name, win_status=win_status)
    db.session.add(user_input)
    db.session.commit()

    move_log = UserInput.query.filter_by(game_id=game_id, game_mode='Double Player').all()

    if win_status:
        return render_template('doubleplayer_end.html', game=Game.layout(), current_player=Game.current_player,message=message, move_log=move_log)


    return render_template('double_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=session['first_move_made'], player1=player1, player2=player2, message=message, move_log=move_log)

@app.route('/single_player')
def single_player():
    if 'game_id' not in session:
        session['game_id'] = str(uuid.uuid4()) 

    first_move_made = session.get('first_move_made', False)
    game_id = session['game_id']
    move_log = UserInput.query.filter_by(game_id=game_id, game_mode='Single Player').all()

    return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=first_move_made, move_log=move_log)


@app.route('/singleplayer_move', methods=['POST'])
def singleplayer_move():
    player = request.form['player']
    position = request.form['position']
    if 'game_id' not in session:
        session['game_id'] = str(uuid.uuid4())
    game_id = session['game_id']
    player_name = "Player" if player == 'X' else "Bot"

    if not position.isdigit() or int(position) not in range(1, 10) or Game.structure[int(position) - 1] != "_":
        error_message = "Invalid move: Please select a valid position."
        move_log = UserInput.query.filter_by(game_id=game_id, game_mode='Single Player').all()
        return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=session.get('first_move_made', False), message=error_message, move_log=move_log)

    message = Game.update(position, player)

    win_status = None
    if "Player X won" in message:
        win_status = "Player Won"
        session['game_id'] = str(uuid.uuid4())
    elif "Player O won" in message:
        win_status = "Bot Won"
        session['game_id'] = str(uuid.uuid4())
    elif "Match Draw!" in message:
        win_status = "Draw"
        session['game_id'] = str(uuid.uuid4())

    user_input = UserInput(game_id=game_id, player=player, position=int(position) - 1, game_mode='Single Player', player_name=player_name, win_status=win_status)
    db.session.add(user_input)
    db.session.commit()

    if not session.get('first_move_made', False):
        session['first_move_made'] = True

    if Game.current_player == 'O' and "won" not in message and "Draw" not in message:
        bot_position, bot_message = Game.bot_move_logic()

        if "Player won" in bot_message:
            win_status = "Player X Won"
            session['game_id'] = str(uuid.uuid4())
        elif "Player O won" in bot_message:
            win_status = "Bot Won"
            session['game_id'] = str(uuid.uuid4())
        elif "Match Draw!" in bot_message:
            win_status = "Draw"
            session['game_id'] = str(uuid.uuid4())

        bot_input = UserInput(game_id=game_id, player='O', position=bot_position, game_mode='Single Player', player_name="Bot", win_status=win_status)
        db.session.add(bot_input)
        db.session.commit()

        message = bot_message

    move_log = UserInput.query.filter_by(game_id=game_id, game_mode='Single Player').all()

    if win_status:
        return render_template('singleplayer_end.html', game=Game.layout(), current_player=Game.current_player,message=message, move_log=move_log)

    return render_template('single_player.html', game=Game.layout(), current_player=Game.current_player, first_move_made=session.get('first_move_made', False), message=message, move_log=move_log)


@app.route('/tutorial')
def tutorial():
    Game.refresh()
    Game.tutorial_logic()
    return render_template('tutorial.html', game=Game.layout(), current_player=Game.current_player)


@app.route('/tutorial_move', methods=['POST'])
def tutorial_move():
    player = request.form['player']
    position = request.form['position']
    game_id = session['game_id']
    message = Game.tutorial_update(position)

    return render_template('tutorial.html', game=Game.layout(), current_player=Game.current_player, message=message)

@app.route('/refresh', methods=['POST'])
def refresh():
    source = request.form.get('source')
    session.pop('game_id', None)
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
