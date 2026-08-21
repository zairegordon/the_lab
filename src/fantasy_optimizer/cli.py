import argparse
from .data import load_players_csv
from .espn_loader import load_players_from_espn
from .optimizer import optimize


def default_roster():
    return {'QB': 1, 'RB': 2, 'WR': 2, 'TE': 1, 'FLEX': 1, 'K': 1, 'DEF': 1}


def main():
    p = argparse.ArgumentParser(description='Fantasy team optimizer')
    p.add_argument('--players', help='CSV file with players')
    p.add_argument('--budget', type=float, default=500, help='Total budget')
    p.add_argument('--espn-league-id', type=int, help='ESPN league id')
    p.add_argument('--espn-year', type=int, default=2026, help='ESPN league year')
    p.add_argument('--espn-s2', help='ESPN espn_s2 cookie value')
    p.add_argument('--espn-swid', help='ESPN SWID cookie value')
    p.add_argument('--espn-freeagents', type=int, default=500, help='Number of free agent players to load')
    args = p.parse_args()

    if args.players:
        players = load_players_csv(args.players)
    elif args.espn_league_id:
        players = load_players_from_espn(
            league_id=args.espn_league_id,
            year=args.espn_year,
            espn_s2=args.espn_s2,
            swid=args.espn_swid,
            size=args.espn_freeagents,
        )
    else:
        raise ValueError('Provide either --players or --espn-league-id with optional ESPN auth values.')

    roster = default_roster()
    team, remaining = optimize(players, roster, args.budget)

    print('Selected team:')
    print(team[['id', 'name', 'position', 'team', 'cost', 'projected_points']].to_string(index=False))
    print(f'Remaining budget: {remaining:.2f}')


if __name__ == '__main__':
    main()
