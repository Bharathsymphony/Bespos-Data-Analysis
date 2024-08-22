import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt


def login_page():
    return html.Div(
    style={
        'backgroundImage': 'url(https://wallpaperaccess.com/full/1624843.jpg)',
        'backgroundSize': 'cover',
        'padding': '20px',
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'height': '100vh'
    },
    children=[
        html.H1("Login", style={'color': '#ffffff'}),
        dcc.Input(id='username', type='text', placeholder='Username', style={'margin': '10px'}),
        dcc.Input(id='password', type='password', placeholder='Password', style={'margin': '10px'}),
        html.Button('Login', id='login-button', n_clicks=0, style={'margin': '10px'}),
        html.Div(id='login-output', style={'color': 'red', 'margin': '10px'})
    ]
)
