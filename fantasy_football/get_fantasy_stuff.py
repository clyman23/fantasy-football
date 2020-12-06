# Some sources
# https://stmorse.github.io/journal/espn-fantasy-v3.html
# https://github.com/cwendt94/espn-api
# http://espn-fantasy-football-api.s3-website.us-east-2.amazonaws.com/

import matplotlib.pyplot as plt
import pandas as pd
import requests

from fantasy_football.visualizations.espn_plotter import ESPNPlotter
from fantasy_football.espn_requests.espn_requests import ESPNRequests


def create_plots() -> dict:
    league_id = 53946782
    year = 2020

    espn_requests = ESPNRequests(league_id, year)

    # Get basic league info
    basic_info = espn_requests.get_league_basic_info()

    teams: list = basic_info["teams"]

    print(teams)

    team_ids = get_team_ids(teams)

    print(team_ids)

    teams_df: pd.DataFrame = pd.DataFrame(
        [
            [team["id"], f"{team['location']} {team['nickname']}", team["abbrev"]]
            for team in teams
        ],
        columns=["id", "team name", "abbrev"]
    )

    teams_df.set_index("id", inplace=True, drop=True)

    print("--------Teams--------")
    print(teams_df)

    # Get matchups info
    matchups = espn_requests.get_league_matchup_info()

    print(matchups.keys())
    print(matchups["schedule"][0].keys())
    print(matchups["teams"][0].keys())

    # Get team matchups and scores
    games_df = [
        [
            game['matchupPeriodId'],
            game['home']['teamId'], game['home']['totalPoints'],
            game['away']['teamId'], game['away']['totalPoints']
        ]
        for game in matchups['schedule']
    ]

    games_df = pd.DataFrame(games_df, columns=['Week', 'Team1', 'Score1', 'Team2', 'Score2'])
    print(games_df.head())

    # Get team margins of victory (or defeat)
    df3 = games_df.assign(
        Margin1 = games_df['Score1'] - games_df['Score2'],
        Margin2 = games_df['Score2'] - games_df['Score1']
    )

    df3 = (
        df3[['Week', 'Team1', 'Margin1']]
        .rename(columns={'Team1': 'Team', 'Margin1': 'Margin'})
        .append(df3[['Week', 'Team2', 'Margin2']]
        .rename(columns={'Team2': 'Team', 'Margin2': 'Margin'}))
    )

    print(df3.head())

    # Get league average scores by week
    avgs = (
        games_df
        .filter(['Week', 'Score1', 'Score2'])
        .melt(id_vars=['Week'], value_name='Score')
        .groupby('Week')
        .mean()
        .reset_index()
    )

    print(avgs)

    team_plots: dict = plot_all_teams(team_ids, teams_df, games_df, avgs)

    return team_plots


def get_team_scores(
        team_id: int,
        all_games_df: pd.DataFrame,
        avg_scores: pd.DataFrame
) -> pd.DataFrame:
    """
    Get points for/against a given team, centered around league average

    Args:
        team_id (int): A given team ID number
        all_games_df (pd.DataFrame): Dataframe of all league game information
        avg_scores (pd.DataFrame): Dataframe of league average score each week
    """
    # grab all games with this team
    team_games_df = all_games_df.query("Team1 == @team_id | Team2 == @team_id").reset_index(
        drop=True
    )

    # move the team of interest to "Team1" column
    ix = list(team_games_df["Team2"] == team_id)
    team_games_df.loc[ix, ['Team1','Score1','Team2','Score2']] = team_games_df.loc[
        ix, ['Team2','Score2','Team1','Score1']
    ].values

    # add new score and win cols
    team_games_df = team_games_df.assign(
        Chg1 = team_games_df['Score1'] - avg_scores['Score'],
        Chg2 = team_games_df['Score2'] - avg_scores['Score'],
        Win  = team_games_df['Score1'] > team_games_df['Score2']
    )

    return team_games_df


def get_team_ids(teams: list) -> list:
    """
    Get list of all team IDs in the league

    Args:
        teams (list): List of dicts of team info

    Returns:
        list: List of all team IDs in the league
    """
    return [team["id"] for team in teams]


def plot_all_teams(
    team_ids: list,
    teams_df: pd.DataFrame,
    games_df: pd.DataFrame,
    avgs: pd.DataFrame
) -> dict:

    espn_plotter = ESPNPlotter()

    team_plots = {}

    for team_id in team_ids:
        team_scores = get_team_scores(team_ids[team_id - 1], games_df, avgs)
        team_name = teams_df.loc[team_ids[team_id - 1]]["team name"]

        team_plots.update(espn_plotter.plot_team_score_analysis(team_scores, team_name))

    return team_plots
