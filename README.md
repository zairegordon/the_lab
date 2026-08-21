# Fantasy Optimizer

A Python starter project to help pick the best fantasy football team.

Web app

This project now includes a Flask web UI served at `http://127.0.0.1:5000/`.

Start the resilient launcher (auto-restarts on crashes):

```bash
run_webapp.bat
```

Or run directly with Python:

```bash
python -m src.fantasy_optimizer.web_app
```

Quick start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Run the CLI with a CSV of players:

```bash
python -m src.fantasy_optimizer.cli --players players.csv --budget 500
```

Project layout

- `src/fantasy_optimizer/optimizer.py`: core team optimizer (ILP with pulp or fallback greedy)
- `src/fantasy_optimizer/data.py`: data loading helpers
- `src/fantasy_optimizer/cli.py`: simple CLI to run optimization
- `tests/`: basic unit test

License: MIT
