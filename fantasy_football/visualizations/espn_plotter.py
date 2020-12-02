"""
Creates ESPN plots
"""
import pandas as pd
import plotly.graph_objects as go


class ESPNPlotter:
    """
    Creates ESPN plots

    Args:
        None

    Attributes:
        None

    Methods:
        plot_team_score_analysis (None): Plots team's and opponent's points compared to average
    """
    def __init__(self):
        pass

    def plot_team_score_analysis(self, team_scores: pd.DataFrame, team_name: str) -> dict:
        """
        Plots team's and opponent's points compared to average

        Args:
            team_scores (pd.DataFrame): Dataframe of a team's scores
            team_name (str): The team's name, used for plotting

        Returns:
            None
        """
        wins = team_scores[team_scores["Win"] == True]
        losses = team_scores[team_scores["Win"] == False]

        pts_for_above_avg_wins = wins["Chg1"].values
        pts_against_above_avg_wins = wins["Chg2"].values

        pts_for_above_avg_losses = losses["Chg1"].values
        pts_against_above_avg_losses = losses["Chg2"].values

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=pts_for_above_avg_wins,
            y=pts_against_above_avg_wins,
            mode="markers",
            name="Wins",
            marker_size=10,
            marker_symbol="circle"
        ))

        fig.add_trace(go.Scatter(
            x=pts_for_above_avg_losses,
            y=pts_against_above_avg_losses,
            mode="markers",
            name="Losses",
            marker_size=10,
            marker_symbol="x"
        ))

        fig.add_trace(go.Scatter(
            x=list(range(-75, 75)),
            y=list(range(-75, 75)),
            mode="lines",
            name="Win/Loss Line"
        ))

        fig.update_layout(
            title="{} Wins and Losses".format(team_name),
            xaxis_title="{} Points Above Average".format(team_name),
            yaxis_title="Opponent Points Above Average"
        )

        fig.update_xaxes(range=[-75, 75])
        fig.update_yaxes(range=[-75, 75])

        return {team_name: fig}
