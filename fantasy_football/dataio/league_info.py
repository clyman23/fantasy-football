"""
Contains class for obtaining league information
"""
import pandas as pd

from fantasy_football.espn_requests.constants import LEAGUE_ID, YEAR
from fantasy_football.espn_requests.espn_requests import ESPNRequests


class LeagueInfo:
    """
    Contains all relevant information for a league

    Args:
        espn_requests (ESPNRequests): Link to communication with ESPN API

    Attribues:
        league_basic_info (dict): Dictionary of basica league information
        league_matchup_info (dict): Dictionary of individual game information

    Methods:
        set_leage_basic_info (None): Sets league_basic_info attribute
        set_leage_matchup_info (None): Sets league_matchup_info attribute
        get_basic_teams_list (list): Returns list of league teams
        get_team_ids (list): Returns list of team ID strings
        get_teams_dataframe (pd.DataFrame): Returns DataFrame of team ID, name, and abbreviation
        get_all_games_df (pd.DataFrame): Returns DataFrame of each game score
        get_all_game_margins (pd.DataFrame): Returns DataFrame of each game margin of victory
        get_weekly_average_score (pd.DataFrame): Returns DataFrame of average score for each week
    """
    def __init__(self, espn_requests: ESPNRequests):
        self._espn_requests: ESPNRequests = espn_requests

        self.league_basic_info: dict = {}
        self.league_matchup_info: dict = {}

    def set_league_basic_info(self) -> None:
        """
        Returns basic league information from ESPN API

        Args:
            None

        Returns:
            None
        """
        self.league_basic_info = self._espn_requests.get_league_basic_info()

    def set_league_matchup_info(self) -> None:
        """
        Returns information about league matchups

        Args:
            None

        Returns:
            None
        """
        self.league_matchup_info = self._espn_requests.get_league_matchup_info()

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

    def get_all_games_df(self) -> pd.DataFrame:
        """
        Gets pandas DataFrame of all game matchup scores

        Args:
            None

        Returns:
            pd.DataFrame: Pandas DataFrame of all game matchup scores
        """
        games_df = [
            [
                game['matchupPeriodId'],
                game['home']['teamId'], game['home']['totalPoints'],
                game['away']['teamId'], game['away']['totalPoints']
            ]
            for game in self.league_matchup_info['schedule']
        ]

        games_df = pd.DataFrame(games_df, columns=['Week', 'Team1', 'Score1', 'Team2', 'Score2'])

        return games_df

    def get_all_game_margins(self) -> pd.DataFrame:
        """
        Get pandas DataFrame of margin of victory (or defeat) for all games

        Args:
            None

        Returns:
            pd.DataFrame: Pandas DataFrame of all game margins
        """
        games_df = self.get_all_games_df()

        game_margins = games_df.assign(
            Margin1 = games_df['Score1'] - games_df['Score2'],
            Margin2 = games_df['Score2'] - games_df['Score1']
        )

        game_margins = (
            game_margins[['Week', 'Team1', 'Margin1']]
            .rename(columns={'Team1': 'Team', 'Margin1': 'Margin'})
            .append(game_margins[['Week', 'Team2', 'Margin2']]
            .rename(columns={'Team2': 'Team', 'Margin2': 'Margin'}))
        )

        return game_margins

    def get_weekly_average_score(self) -> pd.DataFrame:
        """
        Get the average league score for each week

        Args:
            None

        Returns:
            pd.DataFrame: The average team score for every week of the season
        """
        games_df = self.get_all_games_df()

        avgs = (
            games_df
            .filter(['Week', 'Score1', 'Score2'])
            .melt(id_vars=['Week'], value_name='Score')
            .groupby('Week')
            .mean()
            .reset_index()
        )
        
        return avgs
