"""
Getting matchup information for a league
"""
import requests

import pandas as pd

from fantasy_football.espn_requests.constants import BASE_URL


class MatchupInfo:
    """
    Getting matchup information for a league

    Args:
        league_id (int): The ID for the fantasy league
        year (int): The year of the league

    Attributes:
        league_matchup_info (dict): Response from ESPN API of matchup information

    Methods:
        get_league_matchup_info (dict): Returns dict of league matchup information
        get_all_games_df (pd.DataFrame): Returns DataFrame of each game score
        get_all_team_weekly_wins (pd.DataFrame): Get DataFrame of each team's result for each week
        get_all_teams_total_wins (pd.Series): Get Series showing each team's total wins
        get_single_team_total_wins (int): Get the total wins of a given team
        get_all_game_margins (pd.DataFrame): Returns DataFrame of each game margin of victory
        get_weekly_average_score (pd.DataFrame): Returns DataFrame of average score for each week
    """
    def __init__(self, league_id: int, year: int):
        self._league_id: int = league_id
        self._year: int = year

        self._league_url: str = ""

        self.league_matchup_info: dict = {}

    def _get_current_league_url(self) -> None:
        self._league_url = BASE_URL + f"{self._year}/segments/0/leagues/{self._league_id}"

    def get_league_matchup_info(self) -> dict:
        """
        Get a league's matchup information from the ESPN API

        Args:
            None

        Returns:
            dict: Dictionary of matchup information
        """
        if not self._league_url:
            self._get_current_league_url()

        matchups_response = requests.get(self._league_url, params={"view": "mMatchup"})

        self.league_matchup_info = matchups_response.json()

        return matchups_response.json()


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
                game["matchupPeriodId"],
                game["home"]["teamId"],
                game["home"]["totalPoints"],
                game["away"]["teamId"],
                game["away"]["totalPoints"],
                game["winner"]
            ]
            for game in self.league_matchup_info["schedule"]
        ]

        games_df = pd.DataFrame(
            games_df,
            columns=["Week", "Team1", "Score1", "Team2", "Score2", "Winner"]
        )

        return games_df

    def get_all_team_weekly_wins(self) -> pd.DataFrame:
        """
        Get pandas DataFrame showing each team's win/loss result for each week

        Returns:
            pd.DataFrame: df showing each team's (axis 0) win/loss result for each week (axis 1)
        """
        teams_dict = {team.get("id"): {} for team in self.league_matchup_info["teams"]}

        for team in self.league_matchup_info["teams"]:
            team_id = team.get("id")

            for game in self.league_matchup_info["schedule"]:
                if team_id == game["home"]["teamId"] or team_id == game["away"]["teamId"]:
                    if team_id == game["home"]["teamId"]:
                        team_loc = "home"
                    elif team_id == game["away"]["teamId"]:
                        team_loc = "away"

                    teams_dict[team_id][game["matchupPeriodId"]] = int(
                        team_loc == game["winner"].lower()
                    )

        return pd.DataFrame(teams_dict)

    def get_all_teams_total_wins(self) -> pd.Series:
        """
        Get pandas Series showing each team's total wins

        Returns:
            pd.Series: Series giving total wins for each team (Series index is team id)
        """
        weekly_wins = self.get_all_team_weekly_wins()
        return weekly_wins.sum(axis=0)

    def get_single_team_total_wins(self, team_id: int) -> int:
        """
        Get the total number of wins for a single team

        Returns:
            int: Total number of wins for a single team
        """
        all_teams_total_wins = self.get_all_teams_total_wins()
        # TODO: Add exception for when team_id not in all_teams_total_wins
        return all_teams_total_wins[team_id]

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
