from typing import Dict, List
import pandas as pd


def optimize_greedy(players: pd.DataFrame, roster: Dict[str, int], budget: float):
    players = players.copy()
    players['value'] = players['projected_points'] / players['cost'].replace(0, 1e-6)
    selected = []
    remaining_budget = budget

    # Handle fixed positions first (QB, RB, WR, TE, K, DEF)
    for pos, count in roster.items():
        if pos == 'FLEX':
            continue
        pool = players[players['position'] == pos].sort_values('value', ascending=False)
        for _, row in pool.iterrows():
            if len([p for p in selected if p['position'] == pos]) >= count:
                break
            if row['cost'] <= remaining_budget:
                selected.append(row.to_dict())
                remaining_budget -= row['cost']

    # FLEX: allow RB/WR/TE
    flex_count = roster.get('FLEX', 0)
    if flex_count > 0:
        pool = players[players['position'].isin(['RB', 'WR', 'TE'])]
        pool = pool[~pool['id'].isin([p['id'] for p in selected])].sort_values('value', ascending=False)
        for _, row in pool.iterrows():
            if len([p for p in selected if p['position'] in ['RB', 'WR', 'TE']]) >= sum(
                roster.get(p, 0) for p in ['RB', 'WR', 'TE']) + flex_count:
                break
            if len([p for p in selected if p['position'] in ['RB', 'WR', 'TE']]) < sum(
                roster.get(p, 0) for p in ['RB', 'WR', 'TE']):
                # fill required RB/WR/TE spots handled earlier
                pass
            if row['cost'] <= remaining_budget:
                selected.append(row.to_dict())
                remaining_budget -= row['cost']
                if len([p for p in selected if p['position'] in ['RB', 'WR', 'TE']]) >= sum(
                    roster.get(p, 0) for p in ['RB', 'WR', 'TE']) + flex_count:
                    break

    return pd.DataFrame(selected), remaining_budget


def optimize(players: pd.DataFrame, roster: Dict[str, int], budget: float):
    try:
        import pulp
    except Exception:
        return optimize_greedy(players, roster, budget)

    players = players.copy()
    players = players.reset_index(drop=True)
    prob = pulp.LpProblem("fantasy_opt", pulp.LpMaximize)

    x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in players.index]

    # Objective: maximize projected_points
    prob += pulp.lpSum([x[i] * players.loc[i, 'projected_points'] for i in players.index])

    # Budget constraint
    prob += pulp.lpSum([x[i] * players.loc[i, 'cost'] for i in players.index]) <= budget

    # Position constraints
    for pos, count in roster.items():
        if pos == 'FLEX':
            # FLEX can be RB/WR/TE
            prob += pulp.lpSum([x[i] for i in players.index if players.loc[i, 'position'] in ['RB', 'WR', 'TE']]) >= (
                roster.get('RB', 0) + roster.get('WR', 0) + roster.get('TE', 0) + roster.get('FLEX', 0)
            )
        else:
            prob += pulp.lpSum([x[i] for i in players.index if players.loc[i, 'position'] == pos]) == count

    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    selected = players[[v.value() == 1 for v in x]]
    remaining_budget = budget - selected['cost'].sum()
    return selected, remaining_budget
