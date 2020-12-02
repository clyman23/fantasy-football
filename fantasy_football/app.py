"""
Creates plotly dashboard
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

from fantasy_football.get_fantasy_stuff import main

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

team_plots = main()

app.layout = html.Div(style={}, children=[
    html.H1(
        children="Fumble Inn Analytics",
        style={
            "textAlign": "center",
        }
    ),

    html.Div(
        children="Presents insights into the greatest league in all of fantasy football",
        style={
            "textAlign": "center",
        }
    ),

    html.Label("Select Team"),
    dcc.Dropdown(
        options=[
            {"label": "Quentin Quarantino", "value": "Quentin Quarantino"},
            {"label": "Walk into the Room Ertz First", "value": "Walk into the Room Ertz First"},
            {"label": "What’s In A Name?", "value": "What’s In A Name?"},
            {"label": "Ladies And Edelman", "value": "Ladies And Edelman"},
            {"label": "Upstate Billivers",  "value": "Upstate Billivers"},
            {"label": "Cleveland Baker's Boys", "value": "Cleveland Baker's Boys"},
            {"label": "Watt Are Passes?", "value": "Watt Are Passes?"},
            {"label": "Hail Mary", "value": "Hail Mary"},
            {"label": "Daniel Joe 4 Danny Jones!!!", "value": "Daniel Joe 4 Danny Jones!!!"},
            {"label": "UES Stumble WINN", "value": "UES Stumble WINN"},
            {"label": "Cooper Troopers", "value": "Cooper Troopers"},
            {"label": "Taylor Gang", "value": "Taylor Gang"},
        ],
        value='Quentin Quarantino',
        id='my-input',
    ),

    dcc.Graph(
        id='team-graph',
    ),
])

@app.callback(
    Output(component_id='team-graph', component_property='figure'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    return team_plots[input_value]

if __name__ == '__main__':
    app.run_server(debug=True)
