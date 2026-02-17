# Kash Card Game (3-player)

A lightweight Flask application that implements the session-driven scoring logic for a 3-player "Kash" trick-taking game.

Overview
--------
- Three players; each round one player is dealer (rotates). Roles require specific trick counts: dealer=3, suit chooser=8, other=5.
- Players record actual tricks and the server computes missing tricks (points), updates scores, and calculates card-swap instructions for the next round based on extras.
- Game ends when any player reaches or exceeds 21 points.

Features
--------
- Session-based game state: `players`, `scores`, `round_number`, `dealer_index`, `required`, `pending_swaps`.
- Clear routes for starting, playing rounds, viewing results, and resetting the game.
- Modern responsive UI with clean card-based layout.

Requirements
------------
The project uses Flask. Install dependencies from `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

Running locally
---------------
Start the development server:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

Or run directly with Python (development):

```bash
python app.py
```

App Routes
----------
- `/` (GET/POST): Start page — enter 3 player names and initialize session.
- `/round` (GET/POST): Show required tricks, pending swaps; submit actual tricks to compute results.
- `/result` (GET): Show summary of last round, updated scores, and swap instructions.
- `/gameover` (GET): Show loser (player with score >= 21) and final scores.
- `/reset` (GET): Clear session and restart.

Session keys
------------
- `players`: list of 3 player names
- `scores`: dict mapping name -> int
- `round_number`: int
- `dealer_index`: current dealer index (0/1/2)
- `required`: dict mapping name -> required tricks for current round
- `pending_swaps`: dict mapping debtor -> {creditor: count}
- `last_round_missing` / `last_round_actual`: helpers for `/result`

Notes
-----
- This project is intended as a simple demonstration of session-based game state and server-side rule enforcement; the swap instructions are displayed as guidance and not programmatically enforced on card decks.
- To deploy to production, replace the secret key in `app.py` with a secure value and configure a WSGI server (e.g., using `gunicorn`).

Swap instructions wording
------------------------
- Swap instructions now follow this convention: the player who earned the extra tricks (the "winner" for that swap) takes the LOW cards from the other player, and the player who missed tricks (the "loser" for that swap) takes the TOP cards.
- Example: "Khalid swaps 1 card with Massi (Massi takes LOW, Khalid takes TOP)".

License
-------
Unlicensed — use and modify freely for personal projects. If you want a specific license added, tell me which one.

Enjoy! Visit `http://localhost:5000` after starting the app.
# Kash-Card-Game