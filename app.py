from flask import Flask, render_template, redirect, url_for, request, session
from cards import build_deck, identify_remove_pairs
import random
from DBcm import UseDatabase

db_config= {
    'host': 'localhost',
    'database':'gofishDB',
    'user':'gofishuser',
    'password':'gofishpassword',
    #Specifically an issue on college PC \/
    'charset': 'utf8mb4',  
    'collation': 'utf8mb4_general_ci' 
}

app = Flask(__name__)
app.secret_key = 'DlssKvulFvbJoljrlkAolJpwoly' 



def prepare_game_state(message=None):
    return {
        'player': session['player'],
        'computer': session['computer'],
        'player_pairs': session['player_pairs'],
        'computer_pairs': session['computer_pairs'],
        'message': message,
    }

@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        handle = request.form['handle']
        if not handle:
            return render_template('register.html', error="Handle cannot be empty!")
    
        with UseDatabase(db_config) as db:
            print("In Database on register")
            db.execute("INSERT IGNORE INTO players (handle) VALUES (%s)", (handle,))
            db.execute("SELECT id FROM players WHERE handle = %s", (handle,))
            result = db.fetchone()
            if result:
                session['player_id'] = result[0] 
                session['handle'] = handle
                return redirect(url_for('home'))
            else:
                return render_template('register.html', error="Failed to register. Try again.")
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('start.html')

@app.post('/start_game')
def start_game():
    
    deck=build_deck()
    session['deck'] = deck
    session['player']=[deck.pop() for _ in range(7)]
    session['computer']=[deck.pop() for _ in range(7)]
    session['player_pairs']=[]
    session['computer_pairs']=[]
    session['is_player_turn']=True
    session['player'], pairs = identify_remove_pairs(session['player'])
    session['player_pairs'].extend(pairs)
    session['computer'], pairs = identify_remove_pairs(session['computer'])
    session['computer_pairs'].extend(pairs)
    if 'player_id' not in session:
        return redirect(url_for('register'))
    return redirect(url_for('game'))

@app.get('/game')
def game():  
    session['is_player_turn'] = True
    return render_template(
        'game.html', **prepare_game_state()
    )

@app.post('/player_turn')
def player_turn():
    if session['player']:
        selected_card = request.form['selected_card']
        value = selected_card.split(" ")[0]

        match = next((card for card in session['computer'] if card.startswith(value)), None)
        session['successful_requests'] = session.get('successful_requests', 0) + 1
        if match:
            session['player'].append(session['computer'].pop(session['computer'].index(match)))
        else:
            session['failed_requests'] = session.get('failed_requests', 0) + 1
            if session['deck']:
                session['player'].append(session['deck'].pop())
    
    session['player'], player_pairs = identify_remove_pairs(session['player'])
    session['player_pairs'].extend(player_pairs)
    session['computer'], computer_pairs = identify_remove_pairs(session['computer'])
    session['computer_pairs'].extend(computer_pairs)
    
    if not session['player']:
        return redirect(url_for('result', outcome='Player Won! You ran out of Cards'))
    elif not session['computer']:
        return redirect(url_for('result', outcome='Computer Won! Computer ran out of Cards'))
    
    computer_message = computer_turn()

    session['player'], player_pairs = identify_remove_pairs(session['player'])
    session['player_pairs'].extend(player_pairs)
    session['computer'], computer_pairs = identify_remove_pairs(session['computer'])
    session['computer_pairs'].extend(computer_pairs)

    if not session['player']:
        return redirect(url_for('result', outcome='Player Won! You ran out of Cards'))
    elif not session['computer']:
        return redirect(url_for('result', outcome='Computer Won! Computer ran out of Cards'))

    return render_template('partials/game_container.html', **prepare_game_state(computer_message))

def computer_turn():
    session['is_player_turn']=False
    computer_hand = session['computer']
    if computer_hand:
        selected_card = random.choice(computer_hand)
        card_value = selected_card.split(" ")[0]
        session['computer_card_request'] = card_value 
        return f"Computer asks for {card_value}. Do you have it?"
    return "Computer has no cards left to ask for."

@app.post('/computer_request_response')
def computer_request_response():
    print("In computer_request_response")
    response = request.form['response']
    card_value = session['computer_card_request']
    player_hand = session['player']
    computer_hand = session['computer']
    deck = session['deck']

    if response == 'Yes':
        matching_card = next((card for card in player_hand if card.startswith(card_value)), None)
        if matching_card:
            computer_hand.append(player_hand.pop(player_hand.index(matching_card)))
            message = f"Computer took your {matching_card}."
        else:
            if deck:
                new_card = deck.pop()
                computer_hand.append(new_card)
                message = "Computer drew a card."
    else:
        if deck:
            new_card = deck.pop()
            computer_hand.append(new_card)
            message = "Computer drew a card."
    
    # Update pairs for both player and computer
    computer_hand, pairs = identify_remove_pairs(computer_hand)
    session['computer_pairs'].extend(pairs)
    session['player'] = player_hand
    session['computer'] = computer_hand
    session['deck'] = deck
    session['is_player_turn'] = True


    return render_template('game.html', **prepare_game_state(message))

@app.get('/result')
def result():
    winBonus=2
    print("In results")
    outcome = request.args.get('outcome', 'Game Over')
    player_pairs=session.get('player_pairs',[])
    computer_pairs=session.get('computer_pairs',[])

    if len(player_pairs) > len(computer_pairs):
        outcome = 'Player Won! You had more Pairs'
        winner = 'Player'
        winBonus=2
    elif len(player_pairs) < len(computer_pairs):
        outcome = 'Computer Won! Computer had more Pairs'
        winner = 'Computer'
        winBonus=1
    else:
        outcome = "It's a Draw!"

    score = len(player_pairs)*winBonus

    with UseDatabase(db_config) as db:
        try:
            result = db.execute("""INSERT INTO games (player_id, winner, score) VALUES (%s, %s, %s)""", (session['player_id'], winner, score))
            app.logger.debug(f"Insert result: {result}")
        except Exception as e:
            app.logger.error(f"Error inserting into database: {e}")

    return render_template('result.html', outcome=outcome, player_pairs=player_pairs, computer_pairs=computer_pairs)


@app.get('/view_pairs')
def view_pairs():
    player_pairs=session.get('player_pairs',[])
    app.logger.debug(f"Session before view_pairs: {session}")
    return render_template('view_pairs.html', player_pairs=player_pairs)

@app.get('/leaderboard')
def leaderboard():
    with UseDatabase(db_config) as db:
        db.execute("""
            select * from leaderboard;
            """)
        leaderboard_data = db.fetchall()
        leaderboard_data_dict = [
            {
                'handle': row[0],                     # Player's handle
                'games_won': row[1],                  # Number of games won
                'highscore': row[2],                   # Highscore achieved
                'highscore_achieved_at': row[3]       # Timestamp of when highscore was achieved
            }
            for row in leaderboard_data
        ]

    return render_template('leaderboard.html', leaderboard=leaderboard_data_dict)





@app.get('/rules')
def rules():
    return render_template('rules.html')

if __name__ == "__main__":
    app.run(debug=True)