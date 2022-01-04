"""
Creates plotly dashboard
"""
# import dash
# from dash import dcc
# from dash import html
# from dash.dependencies import Input, Output
# import pandas as pd

from fantasy_football.get_fantasy_stuff import get_all_league_info
from fantasy_football.visualizations.dashboard import Dashboard


def main():
    """
    Main function for creating dashboards manually
    """
    team_plots, team_names = get_all_league_info()
    dashboard = Dashboard(team_plots, team_names)
    dashboard.build_app()


if __name__ == '__main__':
    main()
