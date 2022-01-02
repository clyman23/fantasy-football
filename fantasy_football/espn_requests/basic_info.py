"""
Main communication with ESPN fantasy API
"""
import requests

import pandas as pd

from fantasy_football.espn_requests.constants import BASE_URL


class BasicInfo:
    """
    Main communication with ESPN fantasy API

    Args:
        league_id (int): The ID for the fantasy league
        year (int): The year of the league

    Attributes:
        None

    Methods:
        get_league_basic_info (dict): Returns dict of basic league information
        get_basic_teams_list (list): Returns list of league teams
        get_team_ids (list): Returns list of team ID strings
        get_team_name_by_id (str): Returns a team's name based on it's ID
        get_teams_dataframe (pd.DataFrame): Returns DataFrame of team ID, name, and abbreviation
    """
    def __init__(self, league_id: int, year: int):
        self._league_id: int = league_id
        self._year: int = year

        self._league_url: str = ""

        self.league_basic_info: dict = {}
        self.league_matchup_info: dict = {}

    def _get_current_league_url(self) -> None:
        self._league_url = BASE_URL + f"{self._year}/segments/0/leagues/{self._league_id}"

    def get_league_basic_info(self) -> dict:
        """
        Get basic information about the league from the ESPN API

        Args:
            None

        Returns:
            dict: Dictionary of league information from ESPN API
        """
        if not self._league_url:
            self._get_current_league_url()

        basic_info_response = requests.get(self._league_url)

        self.league_basic_info = basic_info_response.json()

        return basic_info_response.json()

    def get_basic_teams_list(self) -> list:
        """
        Returns list of league's teams

        Args:
            None

        Returns:
            list: list of basic team information
        """
        return self.league_basic_info.get("teams", [])

    def get_team_ids(self) -> list:
        """
        Returns list of all league team IDs

        Args:
            None

        Returns:
            list: list of all team IDs
        """
        teams = self.get_basic_teams_list()
        return [team["id"] for team in teams]

    def get_team_name_by_id(self, team_id: int) -> str:
        """
        Returns the name of a team based on it's team ID

        Returns:
            str: The team name
        """
        basic_team_info = self.get_basic_teams_list()

        # TODO: Add check if input team_id doesn't match any "id"s in the basic_team_info
        team_name = ""

        # TODO: More efficient look-up than for loop needed
        for team in basic_team_info:
            if team["id"] == team_id:
                team_name = "{0} {1}".format(team["location"], team["nickname"])

        return team_name

    def get_teams_dataframe(self) -> pd.DataFrame:
        """
        Gets pandas DataFrame of team ID, name, and abbreviation

        Args:
            None

        Returns:
            pd.DataFrame: Pandas DataFrame of team ID, name, and abbreviation
        """
        teams = self.get_basic_teams_list()

        teams_df = pd.DataFrame(
            [
                [team["id"], f"{team['location']} {team['nickname']}", team["abbrev"]]
                for team in teams
            ],
            columns=["id", "team name", "abbrev"]
        )

        teams_df.set_index("id", inplace=True, drop=True)

        return teams_df
