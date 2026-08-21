import argparse
import csv
from typing import List, Dict


def load_players_csv_nopandas(path: str) -> List[Dict]:
    players = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['cost'] = float(row['cost'])
            row['projected_points'] = float(row['projected_points'])
            row['id'] = int(row['id'])
            players.append(row)
    return players


def optimize_greedy_nopandas(players: List[Dict], roster: Dict[str,int], budget: float):
    for p in players:
        cost = p['cost'] if p['cost'] != 0 else 1e-6
        p['value'] = p['projected_points'] / cost
    selected = []
    remaining = budget

    # select fixed positions first
    for pos, count in roster.items():
        if pos == 'FLEX':
            continue
        pool = [p for p in players if p['position'] == pos]
        pool.sort(key=lambda x: x['value'], reverse=True)
        for p in pool:
            if len([s for s in selected if s['position'] == pos]) >= count:
                break
            if p['cost'] <= remaining:
                selected.append(p)
                remaining -= p['cost']

    # FLEX: RB/WR/TE
    flex = roster.get('FLEX', 0)
    if flex > 0:
        pool = [p for p in players if p['position'] in ('RB','WR','TE') and p['id'] not in [s['id'] for s in selected]]
        pool.sort(key=lambda x: x['value'], reverse=True)
        for p in pool:
            if len([s for s in selected if s['position'] in ('RB','WR','TE')]) >= sum(roster.get(k,0) for k in ('RB','WR','TE')) + flex:
                break
            if p['cost'] <= remaining:
                selected.append(p)
                remaining -= p['cost']

    return selected, remaining


def default_roster():
    return {'QB':1,'RB':2,'WR':2,'TE':1,'FLEX':1,'K':1,'DEF':1}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--players', required=True)
    p.add_argument('--budget', type=float, default=500)
    args = p.parse_args()

    players = load_players_csv_nopandas(args.players)
    roster = default_roster()
    team, rem = optimize_greedy_nopandas(players, roster, args.budget)

    print('Selected team:')
    for t in team:
        print(f"{t['id']}: {t['name']} ({t['position']}) - {t['team']} - cost {t['cost']} pts {t['projected_points']}")
    print(f'Remaining budget: {rem:.2f}')

if __name__ == '__main__':
    main()
