from flask import Flask, render_template, request, session, redirect, url_for
import os

from game_logic import determine_required, compute_round, check_loser, rotate_dealer

app = Flask(__name__)
app.secret_key = 'kash_card_game_secret_key'

@app.route('/', methods=['GET', 'POST'])
def start():
    """Start page - enter 3 player names"""
    if request.method == 'POST':
        players = [
            request.form.get('player1', '').strip(),
            request.form.get('player2', '').strip(),
            request.form.get('player3', '').strip(),
        ]
        
        # Validate all players have names
        if not all(players) or len(set(players)) != 3:
            return render_template('start.html', error='All player names must be unique and non-empty')
        
        # Initialize session game state
        session['players'] = players
        session['scores'] = {name: 0 for name in players}
        session['round_number'] = 1
        session['dealer_index'] = 0
        session['pending_swaps'] = {}
        session.modified = True
        
        return redirect(url_for('round_page'))
    
    return render_template('start.html')


@app.route('/round', methods=['GET', 'POST'])
def round_page():
    """Round page - show required tricks and collect actual tricks"""
    
    # Check if game is initialized
    if 'players' not in session:
        return redirect(url_for('start'))
    
    players = session['players']
    dealer_index = session['dealer_index']
    
    if request.method == 'GET':
        # Determine roles and required tricks using shared logic
        required = determine_required(players, dealer_index)
        dealer = players[dealer_index]

        session['required'] = required
        session.modified = True

        return render_template(
            'round.html',
            players=players,
            round_number=session['round_number'],
            dealer=dealer,
            required=required,
            scores=session['scores'],
            pending_swaps=session.get('pending_swaps', {}),
        )
    
    elif request.method == 'POST':
        # Get actual tricks from form
        actual = {}
        for player in players:
            try:
                actual[player] = int(request.form.get(f'tricks_{player}', 0))
            except ValueError:
                actual[player] = 0
        
        required = session.get('required', {})

        # Use shared compute_round to update scores and build pending swaps
        scores = session.get('scores', {})
        scores, missing, pending_swaps = compute_round(scores, players, required, actual)

        session['scores'] = scores
        session['pending_swaps'] = pending_swaps
        session.modified = True

        # Store result info for /result page
        session['last_round_missing'] = missing
        session['last_round_actual'] = actual

        # Check for loser (score >= 21)
        loser = check_loser(session['scores'])
        if loser:
            session['loser'] = loser
            session.modified = True
            return redirect(url_for('gameover'))

        # Prepare for next round
        session['dealer_index'] = rotate_dealer(dealer_index)
        session['round_number'] += 1
        session.modified = True

        return redirect(url_for('result'))


@app.route('/result', methods=['GET'])
def result():
    """Result page - show round summary and swap instructions"""
    
    if 'players' not in session:
        return redirect(url_for('start'))
    
    players = session['players']
    missing = session.get('last_round_missing', {})
    actual = session.get('last_round_actual', {})
    required = session.get('required', {})
    pending_swaps = session.get('pending_swaps', {})
    scores = session['scores']
    
    # Format swap instructions (winner takes LOW, loser takes TOP)
    swap_instructions = []
    for debtor, creditors in pending_swaps.items():
        for creditor, count in creditors.items():
            instruction = f"{debtor} swaps {count} cards with {creditor} ({creditor} takes LOW, {debtor} takes TOP)"
            swap_instructions.append(instruction)
    
    return render_template(
        'result.html',
        players=players,
        round_number=session['round_number'] - 1,  # Show the round we just completed
        missing=missing,
        actual=actual,
        required=required,
        scores=scores,
        swap_instructions=swap_instructions,
    )


@app.route('/gameover', methods=['GET'])
def gameover():
    """Game over page - show loser and final scores"""
    
    if 'players' not in session:
        return redirect(url_for('start'))
    
    loser = session.get('loser', 'Unknown')
    scores = session['scores']
    
    return render_template(
        'gameover.html',
        loser=loser,
        scores=scores,
    )


@app.route('/reset', methods=['GET'])
def reset():
    """Clear session and redirect to start"""
    session.clear()
    return redirect(url_for('start'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
