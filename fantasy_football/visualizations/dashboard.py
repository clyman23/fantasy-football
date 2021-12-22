"""
Contains class to create plotly dashboard
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go


class Dashboard:
    """
    Creates plotly dashboard

    Args:
        team_plots (list): List of team luckiness plots

    Attributes:
        external_stylesheets (list): List of external CSS stylesheets
        app (dash.Dash): Plotly dashboard
        app_children (list): Child elements for the dashboard

    Methods:
        build_app (None): Builds the dashboard
    """
    def __init__(self, team_plots: dict):
        self._team_plots: dict = team_plots

        self.external_stylesheets: list = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app: dash.Dash = dash.Dash(__name__, external_stylesheets=self.external_stylesheets)

        self.app_children: list = []

    def build_app(self) -> None:
        """
        Builds the dashboard

        Args:
            None

        Returns:
            None
        """
        self._build_title()
        self._build_league_standings_table()
        self._build_team_luckiness_children()

        self.app.layout = html.Div(style={}, children=self.app_children)
        self.app.run_server(debug=True)

    def _build_title(self) -> None:
        self.app_children.append(
            html.H1(
                children="Fumble Inn Analytics",
                style={
                    "textAlign": "center",
                }
            )
        )

        self.app_children.append(
            html.Div(
                children="Presents insights into the greatest league in all of fantasy football",
                style={
                    "textAlign": "center",
                }
            )
        )

    def _build_league_standings_table(self) -> None:
        self.app_children.append(
            html.Div([
                self._team_plots["standings"]
            ])
        )

    def _build_team_luckiness_children(self) -> None:
        self.app_children.extend([
            html.Label("Select Team"),

            dcc.Dropdown(
                options=[
                    {"label": "Hips Don't Eli", "value": "Hips Don't Eli"},
                    {"label": "Ertz First", "value": "Ertz First"},
                    {"label": "Toots Town Tacklers", "value": "Toots Town Tacklers"},
                    {"label": "Country Road Take Mahomes", "value": "Country Road Take Mahomes"},
                    {"label": "Mana'Saquon Godwin",  "value": "Mana'Saquon Godwin"},
                    {"label": "Rudolph The Red Zone Reindeer", "value": "Rudolph The Red Zone Reindeer"},
                    {"label": "Taylor’s Titans", "value": "Taylor’s Titans"},
                    {"label": "Hail Mary", "value": "Hail Mary"},
                    {"label": "DB's TD's", "value": "DB's TD's"},
                    {"label": "Masi's Mannings", "value": "Masi's Mannings"},
                ],
                value="Hips Don't Eli",
                id="my-input",
            ),

            dcc.Graph(
                id='team-graph',
            )
        ])

        @self.app.callback(
            Output(component_id='team-graph', component_property='figure'),
            Input(component_id='my-input', component_property='value')
        ) # pylint: disable=W0612
        def update_output_div(input_value: str) -> go.Figure:
            return self._team_plots["luckiness_plots"][input_value]
