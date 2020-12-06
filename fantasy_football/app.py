"""
Creates plotly dashboard
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

from fantasy_football.get_fantasy_stuff import create_plots
from fantasy_football.visualizations.dashboard import Dashboard


def main():
    team_plots = create_plots()
    dashboard = Dashboard(team_plots)
    dashboard.build_app()


if __name__ == '__main__':
    main()
