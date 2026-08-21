from typing import Any, Dict, List, Optional
import pandas as pd


def _player_record(player: Any) -> Dict[str, Any]:
    player_id = getattr(player, 'playerId', None) or getattr(player, 'id', None)
    name = getattr(player, 'name', None) or getattr(player, 'full_name', '')
    position = getattr(player, 'position', None) or getattr(player, 'pos', '') or ''
    team = getattr(player, 'proTeam', None) or getattr(player, 'team', '') or ''
    projected_points = getattr(player, 'projected_avg_points', None)
    if projected_points is None:
        projected_points = getattr(player, 'projected_total_points', None)
    if projected_points is None:
        projected_points = getattr(player, 'avg_points', None)
    if projected_points is None:
        projected_points = 0.0

    cost = getattr(player, 'cost', None)
    if cost is None:
        cost = 1.0

    return {
        'id': player_id,
        'name': name,
        'position': position,
        'team': team,
        'cost': float(cost),
        'projected_points': float(projected_points),
    }


def load_players_from_espn(
    league_id: int,
    year: int,
    espn_s2: Optional[str] = None,
    swid: Optional[str] = None,
    size: int = 500,
) -> pd.DataFrame:
    try:
        from espn_api.football import League
    except ImportError as exc:
        raise ImportError(
            'espn-api is required to load players from ESPN. Install it with `pip install espn-api`.'
        ) from exc

    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid, debug=False)
    records: List[Dict[str, Any]] = []
    seen_ids = set()

    def add_players(players: List[Any]) -> None:
        for player in players:
            record = _player_record(player)
            if record['id'] is None:
                continue
            if record['id'] in seen_ids:
                continue
            if not record['position']:
                continue
            seen_ids.add(record['id'])
            records.append(record)

    # Collect players from team rosters first, then free agents.
    for team in getattr(league, 'teams', []):
        roster = getattr(team, 'roster', None)
        if roster:
            add_players(roster)

    try:
        free_agents = league.free_agents(size=size)
        add_players(free_agents)
    except Exception:
        pass

    if not records:
        raise ValueError('No players were loaded from ESPN. Check league credentials and league settings.')

    df = pd.DataFrame(records)
    expected = {'id', 'name', 'position', 'team', 'cost', 'projected_points'}
    if not expected.issubset(df.columns):
        raise ValueError('Loaded ESPN data does not contain required player fields.')

    return df
