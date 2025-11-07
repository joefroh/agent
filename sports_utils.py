import requests
import requests_cache
from datetime import datetime
from retry_requests import retry


# Sport to league mapping for ESPN API
SPORT_LEAGUE_MAP = {
    "football": {"nfl": "football/nfl"},
    "basketball": {"nba": "basketball/nba"},
    "baseball": {"mlb": "baseball/mlb"},
    "hockey": {"nhl": "hockey/nhl"},
    "soccer": {
        "mls": "soccer/usa.1",
        "premier-league": "soccer/eng.1",
        "la-liga": "soccer/esp.1",
        "bundesliga": "soccer/ger.1",
        "serie-a": "soccer/ita.1",
    },
}


def get_sports_scores(sport, league=None, date=None, team=None):
    """
    Fetches sports scores for a given sport and optional filters.

    Args:
        sport (str): The sport name (e.g., "football", "basketball", "baseball", "hockey", "soccer")
        league (str, optional): The league name (e.g., "nfl", "nba", "mlb", "nhl", "premier-league")
        date (str, optional): Date in YYYY-MM-DD format. Defaults to today if not provided.
        team (str, optional): Filter by specific team name or abbreviation

    Returns:
        dict: A dictionary containing:
            - sport: The sport queried
            - league: The league queried
            - date: The date of scores
            - games: List of game dictionaries with:
                - home_team: Home team name
                - away_team: Away team name
                - home_score: Home team score (if game completed)
                - away_score: Away team score (if game completed)
                - status: Game status (scheduled, in-progress, final)
                - start_time: Game start time
    """
    # Normalize sport name to lowercase
    sport = sport.lower() if sport else None

    # Validate sport
    if sport not in SPORT_LEAGUE_MAP:
        return {
            "error": "Invalid sport name",
            "reason": f"Sport '{sport}' not supported. Supported sports: {', '.join(SPORT_LEAGUE_MAP.keys())}",
        }

    # Determine league if not provided
    if not league:
        # Default to first available league for the sport
        league = list(SPORT_LEAGUE_MAP[sport].keys())[0]
    else:
        league = league.lower()

    # Validate league for sport
    if league not in SPORT_LEAGUE_MAP[sport]:
        return {
            "error": "Invalid league name",
            "reason": f"League '{league}' not supported for {sport}. Supported leagues: {', '.join(SPORT_LEAGUE_MAP[sport].keys())}",
        }

    # Parse date
    if not date:
        date_obj = datetime.now()
    else:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {
                "error": "Invalid date format",
                "reason": "Date must be in YYYY-MM-DD format",
            }

    # Format date for ESPN API (YYYYMMDD)
    date_str = date_obj.strftime("%Y%m%d")

    # Build API path
    api_path = SPORT_LEAGUE_MAP[sport][league]
    url = f"http://site.api.espn.com/apis/site/v2/sports/{api_path}/scoreboard"

    # Setup cache and retry session
    cache_session = requests_cache.CachedSession(
        ".cache", expire_after=300
    )  # 5 min cache
    retry_session = retry(cache_session, retries=3, backoff_factor=0.2)

    try:
        # Make API request
        params = {"dates": date_str}
        response = retry_session.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {
                "error": "API request failed",
                "reason": f"HTTP {response.status_code}: {response.reason}",
            }

        data = response.json()

        # Parse games from response
        games = []
        if "events" in data:
            for event in data["events"]:
                game_info = {
                    "home_team": None,
                    "away_team": None,
                    "home_score": None,
                    "away_score": None,
                    "status": None,
                    "start_time": None,
                }

                # Extract team names and scores
                if "competitions" in event and len(event["competitions"]) > 0:
                    competition = event["competitions"][0]

                    # Get teams
                    if "competitors" in competition:
                        for competitor in competition["competitors"]:
                            team_name = competitor.get("team", {}).get(
                                "displayName", "Unknown"
                            )
                            is_home = competitor.get("homeAway") == "home"
                            score = competitor.get("score")

                            if is_home:
                                game_info["home_team"] = team_name
                                game_info["home_score"] = score
                            else:
                                game_info["away_team"] = team_name
                                game_info["away_score"] = score

                    # Get status
                    game_info["status"] = (
                        competition.get("status", {})
                        .get("type", {})
                        .get("name", "unknown")
                    )

                    # Get start time
                    if "date" in competition:
                        try:
                            # Parse UTC time (Zulu time)
                            utc_time = datetime.fromisoformat(
                                competition["date"].replace("Z", "+00:00")
                            )
                            # Convert to local time
                            local_time = utc_time.astimezone()
                            # Format with UTC offset (more reliable than timezone name)
                            utc_offset = local_time.strftime("%z")
                            if utc_offset:
                                # Format offset as +/-HH:MM
                                offset_str = f"{utc_offset[:3]}:{utc_offset[3:]}"
                            else:
                                offset_str = ""
                            tz_name = local_time.tzname() or offset_str
                            game_info["start_time"] = (
                                local_time.strftime("%Y-%m-%d %H:%M:%S")
                                + f" ({tz_name})"
                            )
                        except Exception:
                            game_info["start_time"] = competition.get("date", "Unknown")

                # Filter by team if specified
                if team:
                    team_lower = team.lower()
                    home_match = (
                        game_info["home_team"]
                        and team_lower in game_info["home_team"].lower()
                    )
                    away_match = (
                        game_info["away_team"]
                        and team_lower in game_info["away_team"].lower()
                    )
                    if not (home_match or away_match):
                        continue

                games.append(game_info)

        result = {
            "sport": sport,
            "league": league,
            "date": date_obj.strftime("%Y-%m-%d"),
            "games": games,
        }

        if not games:
            result["message"] = (
                f"No games found for {sport} ({league}) on {result['date']}"
            )

        return result

    except requests.exceptions.RequestException as e:
        return {
            "error": "Network error",
            "reason": f"Failed to fetch scores: {str(e)}",
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "reason": f"An error occurred: {str(e)}",
        }
