"""
Main communication with ESPN fantasy API
"""
import requests

from fantasy_football.espn_requests.constants import BASE_URL


class ESPNRequests:
    """
    Main communication with ESPN fantasy API

    Args:
        league_id (int): The ID for the fantasy league
        year (int): The year of the league

    Attributes:
        None

    Methods:
        get_league_basic_info (dict): Returns dict of basic league information
        get_league_matchup_info (dict): Returns dict of league matchup information
    """
    def __init__(self, league_id: int, year: int):
        self._league_id: int = league_id
        self._year: int = year

        self._league_url: str = ""

    def _get_current_league_url(self) -> None:
        self._league_url = BASE_URL + f"{self._year}/segments/0/leagues/{self._league_id}"

    def get_league_basic_info(self) -> dict:
        if not self._league_url:
            self._get_current_league_url()

        basic_info_response = requests.get(self._league_url)
        return basic_info_response.json()

    def get_league_matchup_info(self) -> dict:
        if not self._league_url:
            self._get_current_league_url()

        matchups_response = requests.get(self._league_url, params={"view": "mMatchup"})
        return matchups_response.json()
