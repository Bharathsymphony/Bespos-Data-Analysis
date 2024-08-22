
import dash
import dash_html_components as html
import dash_core_components as dcc

app = dash.Dash(__name__)

def nav_bar():
    return html.Div(
        children=[
            html.Div('Supermarket Data Analysis Dashboard', className='nav-brand'),
            html.Div(
                children=[
                    html.A('All Store', href='/dashboard', className='nav-link'),
                    html.A('Specific Page', href='/specific', className='nav-link'),
                    html.A('Logout', href='/login', className='nav-link'),
                ],
                className='navbar-links'
            )
        ],
        className='navbar-container'
    )

def task_bar():
    return html.Div(
        children=[
            html.A('Home', href='/', className='task-link'),
            html.A('Dashboard', href='/dashboard', className='task-link'),
            html.A('Reports', href='/reports', className='task-link'),
            html.A('Settings', href='/settings', className='task-link'),
        ],
        className='taskbar-container'
    )

app.layout = html.Div(
    children=[
        task_bar(),
        html.Div(
            children=[
                nav_bar(),
                html.Div(id='page-content')
            ],
            className='content-container'
        )
    ],
    className='main-container'
)
