import pandas as pd
from src.fantasy_optimizer.optimizer import optimize_greedy


def sample_players():
    data = [
        {'id': 1, 'name': 'QB A', 'position': 'QB', 'team': 'X', 'cost': 50, 'projected_points': 200},
        {'id': 2, 'name': 'RB A', 'position': 'RB', 'team': 'X', 'cost': 60, 'projected_points': 180},
        {'id': 3, 'name': 'RB B', 'position': 'RB', 'team': 'Y', 'cost': 40, 'projected_points': 140},
        {'id': 4, 'name': 'WR A', 'position': 'WR', 'team': 'Z', 'cost': 55, 'projected_points': 160},
        {'id': 5, 'name': 'WR B', 'position': 'WR', 'team': 'Z', 'cost': 45, 'projected_points': 150},
        {'id': 6, 'name': 'TE A', 'position': 'TE', 'team': 'X', 'cost': 30, 'projected_points': 90},
        {'id': 7, 'name': 'K A', 'position': 'K', 'team': 'Y', 'cost': 5, 'projected_points': 50},
        {'id': 8, 'name': 'DEF A', 'position': 'DEF', 'team': 'Y', 'cost': 5, 'projected_points': 45},
    ]
    return pd.DataFrame(data)


def test_greedy_basic():
    players = sample_players()
    roster = {'QB':1,'RB':2,'WR':2,'TE':1,'FLEX':0,'K':1,'DEF':1}
    team, rem = optimize_greedy(players, roster, budget=300)
    assert len(team) == sum(roster.values())
    assert rem >= 0
