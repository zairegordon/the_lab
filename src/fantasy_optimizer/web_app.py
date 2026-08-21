from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template_string, request

from .data import load_players_csv
from .optimizer import optimize

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAYERS_CSV = ROOT / "players.csv"
DEFAULT_BUDGET = 500.0

HTML_TEMPLATE = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Fantasy Optimizer</title>
  <style>
    :root {
      --bg: #f4efe6;
      --card: #fff9f0;
      --ink: #1f2a44;
      --accent: #d65a31;
      --line: #dcc9b1;
    }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background: radial-gradient(circle at top right, #ffe9cc, var(--bg));
      min-height: 100vh;
    }
      .games-ticker {
        display: flex;
        align-items: center;
        gap: 8px;
        overflow: hidden;
        margin: 0 0 12px;
        padding: 5px 10px;
        border: 1px solid rgba(31, 42, 68, 0.08);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(2px);
        color: rgba(31, 42, 68, 0.72);
        font-size: 0.56rem;
        letter-spacing: 0.08em;
        line-height: 1.2;
        text-transform: uppercase;
      }
      .ticker-label {
        flex: 0 0 auto;
        color: rgba(31, 42, 68, 0.72);
        font-weight: 600;
        font-size: 0.56rem;
        letter-spacing: 0.12em;
      }
      .ticker-track {
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: max-content;
        animation: ticker-scroll 24s linear infinite;
      }
      .ticker-game {
        white-space: nowrap;
        font-size: 0.54rem;
        opacity: 0.8;
      }
      .ticker-game::after {
        content: "•";
        margin-left: 10px;
        color: rgba(214, 90, 49, 0.6);
      }
      @keyframes ticker-scroll {
        from { transform: translateX(0); }
        to { transform: translateX(-35%); }
      }
      @media (prefers-reduced-motion: reduce) {
        .ticker-track { animation: none; }
      }
    .wrap {
      max-width: 980px;
      margin: 24px auto;
      padding: 0 16px 36px;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 8px 24px rgba(31, 42, 68, 0.08);
    }
    h1 {
      margin: 0 0 10px;
      letter-spacing: 0.4px;
    }
    form {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      align-items: end;
    }
    label {
      font-size: 0.92rem;
      display: block;
      margin-bottom: 6px;
    }
    input {
      width: 100%;
      box-sizing: border-box;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      font: inherit;
      background: #fff;
    }
    button {
      padding: 11px 14px;
      border: 0;
      border-radius: 10px;
      background: var(--accent);
      color: #fff;
      font-weight: 700;
      cursor: pointer;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 16px;
      font-size: 0.95rem;
      background: #fff;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 8px;
      text-align: left;
      white-space: nowrap;
    }
    .error {
      margin-top: 14px;
      color: #9d1d00;
      font-weight: 700;
    }
    .meta {
      margin-top: 10px;
      font-size: 0.95rem;
      color: #4a5774;
    }
  </style>
</head>
<body>
  <main class=\"wrap\">
    <section class=\"card\">
      <div class="games-ticker" aria-label="Upcoming games">
        <div class="ticker-track">
          <span class="ticker-game">Thu 8:20 PM: Ravens at Bengals</span>
          <span class="ticker-game">Sun 1:00 PM: Bills at Dolphins</span>
          <span class="ticker-game">Sun 4:25 PM: 49ers at Rams</span>
          <span class="ticker-game">Mon 8:15 PM: Chiefs at Raiders</span>
        </div>
      </div>
      <h1>The Lab</h1>
      <form method=\"post\">
        <div>
          <label for=\"players\">Players CSV path</label>
          <input id=\"players\" name=\"players\" value=\"{{ players_path }}\" required />
        </div>
        <div>
          <label for=\"budget\">Budget</label>
          <input id=\"budget\" name=\"budget\" value=\"{{ budget }}\" required />
        </div>
        <div>
          <button type=\"submit\">Optimize</button>
        </div>
      </form>

      {% if error %}
      <div class=\"error\">{{ error }}</div>
      {% endif %}

      {% if team %}
      <div class=\"meta\">Remaining budget: {{ remaining }}</div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Pos</th>
            <th>Team</th>
            <th>Cost</th>
            <th>Projected</th>
          </tr>
        </thead>
        <tbody>
        {% for row in team %}
          <tr>
            <td>{{ row.id }}</td>
            <td>{{ row.name }}</td>
            <td>{{ row.position }}</td>
            <td>{{ row.team }}</td>
            <td>{{ row.cost }}</td>
            <td>{{ row.projected_points }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
      {% endif %}
    </section>
  </main>
</body>
</html>
"""


def default_roster() -> dict[str, int]:
    return {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DEF": 1}


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.route("/", methods=["GET", "POST"])
    def index() -> str:
        players_path = str(DEFAULT_PLAYERS_CSV)
        budget = DEFAULT_BUDGET
        team: list[dict] = []
        remaining = ""
        error = ""

        if request.method == "POST":
            players_path = request.form.get("players", players_path).strip()
            budget_text = request.form.get("budget", str(DEFAULT_BUDGET)).strip()
            try:
                budget = float(budget_text)
                players = load_players_csv(players_path)
                optimized_team, remaining_budget = optimize(players, default_roster(), budget)
                team = optimized_team[["id", "name", "position", "team", "cost", "projected_points"]].to_dict("records")
                remaining = f"{remaining_budget:.2f}"
            except Exception as ex:
                error = str(ex)

        return render_template_string(
            HTML_TEMPLATE,
            players_path=players_path,
            budget=budget,
            team=team,
            remaining=remaining,
            error=error,
        )

    return app


def main() -> None:
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
