import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from login import login_page
from dashboard import dashboard_page
from specific_page import specific_page

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.css.append_css({'external_url': 'assets/styles.css'})

# Define the app layout with conditional rendering
app.layout = html.Div(
    id='main-container',
    children=[
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ]
)

# Callback to handle login and switch to the dashboard
@app.callback(
    Output('url', 'pathname'),
    [Input('login-button', 'n_clicks')],
    [State('username', 'value'), State('password', 'value')]
)
def display_page(n_clicks, username, password):
    if n_clicks:
        # Simple authentication (replace with your own logic)
        if username == 'admin' and password == 'password':
            return '/dashboard'
    return '/login'

# Callback to render the appropriate page content
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def render_page_content(pathname):
    if pathname == '/dashboard':
        return dashboard_page()
    elif pathname == '/specific':
        return specific_page()
    else:
        return login_page()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

