# Some sources
# https://stmorse.github.io/journal/espn-fantasy-v3.html
# https://github.com/cwendt94/espn-api
# http://espn-fantasy-football-api.s3-website.us-east-2.amazonaws.com/

import dash_table
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import requests

from fantasy_football.dataio.league_info import LeagueInfo
from fantasy_football.visualizations.espn_plotter import ESPNPlotter
from fantasy_football.espn_requests.espn_requests import ESPNRequests


def create_plots() -> dict:
    league_id = 53946782
    year = 2020

    espn_requests = ESPNRequests(league_id, year)

    league_info = LeagueInfo(espn_requests)
    league_info.set_league_basic_info()
    league_info.set_league_matchup_info()

    team_ids = league_info.get_team_ids()

    teams_df = league_info.get_teams_dataframe()

    games_df = league_info.get_all_games_df()

    avgs = league_info.get_weekly_average_score()

    all_teams_total_wins = league_info.get_all_teams_total_wins()

    figures = {}

    figures.update(tabulate_league_standings(league_info, team_ids, all_teams_total_wins))

    figures.update(plot_all_teams(team_ids, teams_df, games_df, avgs))

    return figures


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


def tabulate_league_standings(
    league_info: LeagueInfo,
    team_ids: list,
    all_teams_total_wins: pd.Series
) -> dict:
    sorted_total_wins = all_teams_total_wins.sort_values(ascending=False)

    total_games = 15

    sorted_total_losses = total_games - sorted_total_wins

    sorted_total_win_losses = pd.DataFrame(
        {"Wins": sorted_total_wins, "Losses": sorted_total_losses}
    )

    team_names = {
        team_id: league_info.get_team_name_by_id(team_id) for team_id in sorted_total_win_losses.index
    }

    sorted_total_win_losses["Team Name"] = pd.Series(team_names, index=sorted_total_win_losses.index)
    sorted_total_win_losses.fillna("No Name", inplace=True)

    data_table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in sorted_total_win_losses.columns],
        data=sorted_total_win_losses.to_dict("records")
    )

    return {"standings": data_table}


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

    return {"luckiness_plots": team_plots}
