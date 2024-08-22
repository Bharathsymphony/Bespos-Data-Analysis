import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from nav import nav_bar
import io
import base64
from datetime import datetime, timedelta
import random
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
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


# Load your datasets
transaction_data = pd.read_csv('Dataset/TRANSACTION.csv')
transaction_product_data = pd.read_csv('Dataset/transaction_product_data_1a.csv')
product_data = pd.read_csv('Dataset/PRODUCT.csv')
product_batch_data= pd.read_csv('Dataset/PRODUCT_BATCH_data.csv')
pair_df=pd.read_csv('Dataset/pairs_df.csv')

transaction_data.rename(columns={'id': 'transaction_id'}, inplace=True)
# Calculate repeat customers for each store
repeat_customers_by_store = transaction_data.groupby('store_outlet_id')['customer_id'].nunique()

# Sort by number of repeat customers in descending order
top_stores_by_repeat_customers = repeat_customers_by_store.sort_values(ascending=False)

# Prepare data for visualization
top_stores = top_stores_by_repeat_customers.head(10).reset_index()
top_stores.columns = ['Store ID', 'Repeat Customers']
top_stores['Store ID']=top_stores['Store ID'].astype(str)

# Calculate average transaction value by store
transaction_data=transaction_data[transaction_data['net_amount']>0]
average_transaction_value_by_store = transaction_data.groupby('store_outlet_id')['net_amount'].mean().reset_index()
average_transaction_value_by_store.columns = ['Store ID', 'Average Transaction Value']
average_transaction_value_by_store['Store ID']=average_transaction_value_by_store['Store ID'].astype(str)

store_ids = [str(store_id) for store_id in average_transaction_value_by_store['Store ID']]

# Function to calculate high-demand products in a specific time period by store
def product_with_high_demand_in_specific_time_period(transaction_product_data, store_id, product_data):
    # Filter the data for the desired time period and store
    transaction_product_data['transaction_date'] = pd.to_datetime(transaction_product_data['transaction_date'])
    start_date = pd.to_datetime('2021-01-01')
    end_date = pd.to_datetime('2021-12-31')

    filtered_data = transaction_product_data[(transaction_product_data['transaction_date'] >= start_date) & (transaction_product_data['transaction_date'] <= end_date) & (transaction_product_data['Store_outlet_id'] == store_id)]

    # Group the data by product ID and calculate the sum of quantities sold
    product_sales = filtered_data.groupby('product_id')['qty'].sum().sort_values(ascending=False)

    # Get the top 10 products with the highest sales
    high_demand_products = product_sales.head(10)

    # Prepare data for the bar chart
    product_ids = high_demand_products.index.to_list()
    product_names = [product_data[product_data['id'] == product_id]['name'].values[0] for product_id in product_ids]
    quantities = high_demand_products.values.tolist()

    return product_names, quantities
# Get high demand products for a specific store (example: store_id=2)
store_id = 2
product_names, quantities = product_with_high_demand_in_specific_time_period(transaction_product_data, store_id, product_data) 

def sales_growth_in_specific_time_period(transaction_data):
    # Filter data by the desired time period
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    filtered_data = transaction_data[(transaction_data['transaction_date'] >= start_date) & (transaction_data['transaction_date'] <= end_date)]

    # Calculate the total sales for each store
    store_sales = filtered_data.groupby('store_outlet_id')['net_amount'].sum()

    # Calculate the total sales for each store in the previous time period
    previous_start_date = '2022-01-01'
    previous_end_date = '2022-12-31'

    previous_filtered_data = transaction_data[(transaction_data['transaction_date'] >= previous_start_date) & (transaction_data['transaction_date'] <= previous_end_date)]

    previous_store_sales = previous_filtered_data.groupby('store_outlet_id')['net_amount'].sum()

    # Calculate the sales growth for each store
    growth_by_store = (store_sales - previous_store_sales) / previous_store_sales * 100

    # Convert to DataFrame for easier manipulation
    growth_df = pd.DataFrame({
        'Store ID': growth_by_store.index,
        'Sales Growth (%)': growth_by_store.values
    })

    return growth_df

# Function to calculate average customer traffic in a year
def average_customer_traffic_in_a_year(transaction_data, year):
    # Convert 'transaction_date' to datetime
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])

    # Filter data for the specified year
    transaction_data_year = transaction_data[transaction_data['transaction_date'].dt.year == year]

    # Group data by store ID and month
    grouped_data = transaction_data_year.groupby(['store_outlet_id', pd.Grouper(key='transaction_date', freq='M')]).size()

    # Calculate average customer traffic per month
    average_traffic_by_store = grouped_data.groupby(level=0).mean().reset_index()
    average_traffic_by_store.columns = ['Store ID', 'Average Traffic']

    return average_traffic_by_store

# Calculate initial average customer traffic data for 2023
initial_average_traffic_data = average_customer_traffic_in_a_year(transaction_data, 2023)
initial_average_traffic_data['Store ID'] = initial_average_traffic_data['Store ID'].astype(str)


# Function to calculate average transaction value by store in a specific month
def average_transaction_value_by_store_in_specific_month(transaction_data, year, month):
    # Convert 'transaction_date' to datetime
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])

    # Filter data for the specified year and month
    transaction_data_filtered = transaction_data[(transaction_data['transaction_date'].dt.year == year) & (transaction_data['transaction_date'].dt.month == month)]

    # Check if the filtered DataFrame is empty
    if transaction_data_filtered.empty:
        return pd.DataFrame(), None

    # Calculate average transaction value by store
    average_transaction_value_by_store = transaction_data_filtered.groupby('store_outlet_id')['net_amount'].mean().reset_index()
    average_transaction_value_by_store.columns = ['Store ID', 'Average Transaction Value']

    return average_transaction_value_by_store, pd.to_datetime(f'{year}-{month}-01').strftime('%B')

# Calculate initial average transaction value data for a specific month
average_transaction_value_data, month_name = average_transaction_value_by_store_in_specific_month(transaction_data, 2022, 4)
average_transaction_value_data['Store ID'] = average_transaction_value_data['Store ID'].astype(str)

# print("Hi")
# print(average_transaction_value_data.info())
# Function to calculate average basket size in a specific month
def average_basket_size_specific_month(transaction_data, transaction_product_data_1a, year, month):
    # Convert 'transaction_date' to datetime
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])

    # Filter data for the specified year and month
    transaction_data_filtered = transaction_data[(transaction_data['transaction_date'].dt.year == year) & (transaction_data['transaction_date'].dt.month == month)]

    # Check if the filtered DataFrame is empty
    if transaction_data_filtered.empty:
        return pd.DataFrame(), None

    # Merge transaction and product data
    transaction_product_datas = pd.merge(transaction_data_filtered, transaction_product_data_1a, on='transaction_id', how='left')

    # Calculate the average number of items purchased per transaction for each store
    average_items_per_transaction = transaction_product_datas.groupby('store_outlet_id')['total_qty'].mean().reset_index()
    average_items_per_transaction.columns = ['Store ID', 'Average Items per Transaction']

    return average_items_per_transaction, pd.to_datetime(f'{year}-{month}-01').strftime('%B')

# Calculate initial average basket size data for a specific month
average_basket_size_data, basket_month_name = average_basket_size_specific_month(transaction_data, transaction_product_data, 2022, 2)
average_basket_size_data['Store ID'] = average_basket_size_data['Store ID'].astype(str)


def profit_in_each_store_by_year(transaction_product, year):
    # Filter data for the specified year
    transaction_product['transaction_date'] = pd.to_datetime(transaction_product['transaction_date'])
    transaction_data_filtered = transaction_product[transaction_product['transaction_date'].dt.year == year]

    # Calculate profit for each transaction
    transaction_data_filtered['profit'] = (transaction_data_filtered['sales_price'] - transaction_data_filtered['rate']) * transaction_data_filtered['qty']
    
    # Group by store ID and sum the profits
    profit_by_store = transaction_data_filtered.groupby('Store_outlet_id')['profit'].sum().reset_index()
    profit_by_store.columns = ['Store ID', 'Profit']

    return profit_by_store
# Calculate initial profit data for the year 2022
profit_data_2022 = profit_in_each_store_by_year(transaction_product_data, 2022)
profit_data_top_stores = profit_data_2022[profit_data_2022['Store ID'] > 65].sort_values('Store ID')
profit_data_bottom_stores = profit_data_2022[profit_data_2022['Store ID'] <= 65].sort_values('Store ID')
profit_data_bottom_stores['Store ID']=profit_data_bottom_stores['Store ID'].astype(str)

# Calculate initial profit data for 2022
top_stores_profit, bottom_stores_profit = profit_in_each_store_by_year(transaction_product_data, 2022)

# Initialize the Dash app
# app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Calculate sales growth data
growth_data = sales_growth_in_specific_time_period(transaction_data)
growth_data['Store ID']=growth_data['Store ID'].astype(str)


def dashboard_page():
    return html.Div(
        style={
            'backgroundImage': 'url(https://th.bing.com/th/id/OIP.JYQmuMe6R4uEJzhmN8Tj3gHaL4?pid=ImgDet&w=179&h=288&c=7&dpr=1.3)',
            'backgroundSize': 'cover',
            'padding': '20px'
        },
        children=[
            nav_bar(),
            html.H1(
                "Analysis over all Store",
                style={'textAlign': 'center', 'color': '#ffffff', 'backgroundColor': 'rgba(0, 0, 0, 0.5)', 'padding': '10px'}
            ),
            
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px 0'},
                children=[
                    # Graph component to display the top stores with most repeat customers
                    dcc.Graph(
                        id='top-stores-repeat-customers',
                        figure=px.bar(
                            top_stores,
                            x='Store ID',
                            y='Repeat Customers',
                            title="Top Stores with Most Repeat Customers",
                            text='Repeat Customers',
                            color='Repeat Customers',
                            color_continuous_scale=px.colors.sequential.Plasma
                        ).update_traces(
                            texttemplate='%{text:.2s}',
                            textposition='outside',
                            marker=dict(line=dict(color='#333', width=1))
                        ).update_layout(
                            title={'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                            xaxis=dict(title='Store ID', tickmode='linear'),
                            yaxis=dict(title='Number of Repeat Customers'),
                            plot_bgcolor='rgba(255, 255, 255, 0.8)',
                            paper_bgcolor='rgba(255, 255, 255, 0.8)',
                            font=dict(color='#333'),
                            hovermode='x'
                        )
                    ),
                    
                    # Graph component to display the average transaction value by store
                    dcc.Graph(
                        id='average-transaction-value-by-store',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=average_transaction_value_by_store['Store ID'],
                                    y=average_transaction_value_by_store['Average Transaction Value'],
                                    text=average_transaction_value_by_store['Average Transaction Value'].apply(lambda x: f'{x:.2f}'),
                                    textposition='outside',
                                    marker=dict(color='rgb(255,127,14)', line=dict(color='rgb(0,0,0)', width=1.5))
                                )
                            ],
                            layout=go.Layout(
                                title='Average Transaction Value by Store',
                                xaxis=dict(title='Store ID', tickmode='linear'),
                                yaxis=dict(title='Average Transaction Value'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333'),
                                hovermode='x'
                            )
                        )
                    ),
                ]
            ),

            html.Div(
                style={'display': 'flex', 'margin': '20px 0', 'justifyContent': 'space-around'},
                children=[
                    # Graph component to display high-demand products in a specific time period by store
                    dcc.Graph(
                        id='high-demand-products',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=quantities,
                                    y=product_names,
                                    orientation='h',
                                    text=quantities,
                                    textposition='outside',
                                    marker=dict(color=px.colors.sequential.Magma)
                                )
                            ],
                            layout=go.Layout(
                                title=f'Top 10 High Demand Products in Store {store_id} (2021-01-01 to 2021-12-31)',
                                xaxis=dict(title='Quantity Sold'),
                                yaxis=dict(title='Product Name'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333'),
                                hovermode='y'
                            )
                        )
                    ),

                    # Graph component to display sales growth by store
                    dcc.Graph(
                        id='sales-growth-bar-chart',
                        figure={
                            'data': [
                                go.Bar(
                                    x=growth_data['Store ID'],
                                    y=growth_data['Sales Growth (%)'],
                                    text=growth_data['Sales Growth (%)'].apply(lambda x: f'{x:.2f}%'),
                                    textposition='outside',
                                    marker=dict(color='rgb(44,160,44)', line=dict(color='rgb(31,119,180)', width=1.5))
                                )
                            ],
                            'layout': go.Layout(
                                title=f'Sales Growth',
                                xaxis=dict(title='Store ID', tickmode='linear'),
                                yaxis=dict(title='Sales Growth (%)'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333'),
                                hovermode='x'
                            )
                        }
                    ),
                ]
            ),

            html.Div(
                style={'margin': '20px'},
                children=[
                    # Graph component to display average customer traffic by store in a year
                    dcc.Graph(
                        id='average-customer-traffic-bar-chart',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=initial_average_traffic_data['Store ID'],
                                    y=initial_average_traffic_data['Average Traffic'],
                                    text=initial_average_traffic_data['Average Traffic'].apply(lambda x: f'{x:.2f}'),
                                    textposition='outside',
                                    marker=dict(color='rgb(31,119,180)', line=dict(color='rgb(214,39,40)', width=1.5))
                                )
                            ],
                            layout=go.Layout(
                                title='Average Customer Traffic by Store in 2023',
                                xaxis=dict(title='Store ID', tickmode='linear'),
                                yaxis=dict(title='Average Traffic'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333'),
                                hovermode='x'
                            )
                        )
                    )
                ]
            ),
            
            html.Div(
                style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '20px'},
                children=[
                    dcc.DatePickerSingle(
                        id='date-picker',
                        min_date_allowed=transaction_data['transaction_date'].min().date(),
                        max_date_allowed=transaction_data['transaction_date'].max().date(),
                        initial_visible_month=transaction_data['transaction_date'].min().date(),
                        date=transaction_data['transaction_date'].min().date()
                    ),
                    html.Button('Update', id='update-button', n_clicks=0, style={'marginLeft': '10px'})
                ]
            ),
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-around'},
                children=[
                    dcc.Graph(
                        id='average-transaction-value-by-store-month',
                        figure={
                            'data': [
                                go.Bar(
                                    x=average_transaction_value_data['Store ID'],
                                    y=average_transaction_value_data['Average Transaction Value'],
                                    text=average_transaction_value_data['Average Transaction Value'].apply(lambda x: f'{x:.2f}'),
                                    textposition='outside',
                                    marker=dict(color='rgb(6,27,252)', line=dict(color='rgb(0,0,0)', width=1.5))
                                )
                            ],
                            'layout': go.Layout(
                                title=f'Average Transaction Value by Store in {month_name}',
                                xaxis=dict(title='Store ID', tickmode='linear'),
                                yaxis=dict(title='Average Transaction Value'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333'),
                                hovermode='x'
                            )
                        }
                    ),
                    # Graph component to display the average basket size by store in a specific month
                    dcc.Graph(
                        id='average-basket-size-by-store-month',
                        figure={
                            'data': [
                                go.Bar(
                                    x=average_basket_size_data['Store ID'],
                                    y=average_basket_size_data['Average Items per Transaction'],
                                    text=average_basket_size_data['Average Items per Transaction'].apply(lambda x: f'{x:.2f}'),
                                    textposition='outside',
                                    marker=dict(color='rgb(148,103,189)', line=dict(color='rgb(140,86,75)', width=1.5))
                                )
                            ],
                            'layout': go.Layout(
                                title=f'Average Basket Size by Store in {basket_month_name}',
                                xaxis=dict(title='Store ID', tickmode='linear'),
                                yaxis=dict(title='Average Items per Transaction'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333'),
                                hovermode='x'
                            )
                        }
                    )
                ]
            ),

            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-around','marginBottom': '20px 0'},
                children=[
                    # Graph component to display the profit by store for the year 2022 (Store IDs > 65)
                    dcc.Graph(
                        id='profit-by-store-bottom',
                        figure={
                            'data': [
                                go.Bar(
                                    x=profit_data_bottom_stores['Store ID'],
                                    y=profit_data_bottom_stores['Profit'],
                                    text=profit_data_bottom_stores['Profit'].apply(lambda x: f'{x:.2f}'),
                                    textposition='outside',
                                    marker=dict(color='rgb(50,205,50)', line=dict(color='rgb(34,139,34)', width=1.5))
                                )
                            ],
                            'layout': go.Layout(
                                title='Profit in 2022(ID < 65)',
                                xaxis=dict(title='Store ID', tickmode='linear'),
                                yaxis=dict(title='Profit'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333'),
                                hovermode='x'
                            )
                        }
                    ),
                    dcc.Graph(
                        id='profit-by-store-top',
                        figure={
                            'data': [
                                go.Bar(
                                    x=profit_data_top_stores['Store ID'],
                                    y=profit_data_top_stores['Profit'],
                                    text=profit_data_top_stores['Profit'].apply(lambda x: f'{x:.2f}'),
                                    textposition='outside',
                                    marker=dict(color='rgb(255,69,0)', line=dict(color='rgb(170,0,0)', width=1.5))
                                )
                            ],
                            'layout': go.Layout(
                                title='Profit in 2022(ID > 65)',
                                xaxis=dict(title='Store ID', tickmode='linear'),
                                yaxis=dict(title='Profit'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333'),
                                hovermode='x'
                            )
                        }
                    ),
                ]
            ),
        ]
    )

app = dash.Dash(__name__)

app.layout = dashboard_page()

@app.callback(
    Output('average-transaction-value-by-store-month', 'figure'),
    [Input('update-button', 'n_clicks')],
    [State('date-picker', 'date')]
)
def update_graph(n_clicks, selected_date):
    if not selected_date:
        return dash.no_update

    selected_date = pd.to_datetime(selected_date)
    year = selected_date.year
    month = selected_date.month

    average_transaction_value_data, month_name = average_transaction_value_by_store_in_specific_month(transaction_data, year, month)
    if average_transaction_value_data.empty:
        return {
            'data': [],
            'layout': go.Layout(
                title=f'No data available for {month_name} {year}',
                xaxis=dict(title='Store ID', tickmode='linear'),
                yaxis=dict(title='Average Transaction Value'),
                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                font=dict(color='#333'),
                hovermode='x'
            )
        }

    average_transaction_value_data['Store ID'] = average_transaction_value_data['Store ID'].astype(str)
    
    return {
        'data': [
            go.Bar(
                x=average_transaction_value_data['Store ID'],
                y=average_transaction_value_data['Average Transaction Value'],
                text=average_transaction_value_data['Average Transaction Value'].apply(lambda x: f'{x:.2f}'),
                textposition='outside',
                marker=dict(color='rgb(6,27,252)', line=dict(color='rgb(0,0,0)', width=1.5))
            )
        ],
        'layout': go.Layout(
            title=f'Average Transaction Value by Store in {month_name} {year}',
            xaxis=dict(title='Store ID', tickmode='linear'),
            yaxis=dict(title='Average Transaction Value'),
            plot_bgcolor='rgba(255, 255, 255, 0.8)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)',
            font=dict(color='#333'),
            hovermode='x'
        )
    }


@app.callback(
    Output('average-basket-size-by-store-month', 'figure'),
    [Input('basket-date-picker', 'date')]
)
def update_average_basket_size_graph(date):
    year, month, _ = date.split('-')
    average_basket_size_data, basket_month_name = average_basket_size_specific_month(transaction_data, transaction_product_data_1a, int(year), int(month))
    
    if average_basket_size_data.empty:
        return {
            'data': [],
            'layout': go.Layout(
                title=f'No Data Available for {basket_month_name}',
                xaxis=dict(title='Store ID', tickmode='linear'),
                yaxis=dict(title='Average Items per Transaction'),
                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                font=dict(color='#333')
            )
        }

    return {
        'data': [
            go.Bar(
                x=average_basket_size_data['Store ID'],
                y=average_basket_size_data['Average Items per Transaction'],
                text=average_basket_size_data['Average Items per Transaction'].apply(lambda x: f'{x:.2f}'),
                textposition='outside',
                marker=dict(color='rgb(158,202,225)', line=dict(color='rgb(8,48,107)', width=1.5))
            )
        ],
        'layout': go.Layout(
            title=f'Average Basket Size by Store in {basket_month_name}',
            xaxis=dict(title='Store ID', tickmode='linear'),
            yaxis=dict(title='Average Items per Transaction'),
            plot_bgcolor='rgba(255, 255, 255, 0.8)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)',
            font=dict(color='#333')
        )
    }

@app.callback(
    [Output('profit-by-store-top', 'figure'),
     Output('profit-by-store-bottom', 'figure')],
    [Input('year-dropdown', 'value')]
)
def update_profit_graphs(year):
    profit_data = profit_in_each_store_by_year(transaction_product, year)
    profit_data_top_stores = profit_data[profit_data['Store ID'] > 65].sort_values('Store ID')
    profit_data_bottom_stores = profit_data[profit_data['Store ID'] <= 65].sort_values('Store ID')

    top_figure = {
        'data': [
            go.Bar(
                x=profit_data_top_stores['Store ID'],
                y=profit_data_top_stores['Profit'],
                text=profit_data_top_stores['Profit'].apply(lambda x: f'{x:.2f}'),
                textposition='outside',
                marker=dict(color='rgb(158,202,225)', line=dict(color='rgb(8,48,107)', width=1.5))
            )
        ],
        'layout': go.Layout(
            title=f'Stores with ID > 65 by Profit in {year}',
            xaxis=dict(title='Store ID', tickmode='linear'),
            yaxis=dict(title='Profit'),
            plot_bgcolor='rgba(255, 255, 255, 0.8)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)',
            font=dict(color='#333')
        )
    }

    bottom_figure = {
        'data': [
            go.Bar(
                x=profit_data_bottom_stores['Store ID'],
                y=profit_data_bottom_stores['Profit'],
                text=profit_data_bottom_stores['Profit'].apply(lambda x: f'{x:.2f}'),
                textposition='outside',
                marker=dict(color='rgb(158,202,225)', line=dict(color='rgb(8,48,107)', width=1.5))
            )
        ],
        'layout': go.Layout(
            title=f'Stores with ID <= 65 by Profit in {year}',
            xaxis=dict(title='Store ID', tickmode='linear'),
            yaxis=dict(title='Profit'),
            plot_bgcolor='rgba(255, 255, 255, 0.8)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)',
            font=dict(color='#333')
        )
    }

    return top_figure, bottom_figure


transaction_data.rename(columns={'id': 'transaction_id'}, inplace=True)

# Function to calculate high-demand products in a specific time period by store
def product_with_high_demand_in_specific_time_period(transaction_product_data, store_id, product_data):
    # Filter the data for the desired time period and store
    transaction_product_data['transaction_date'] = pd.to_datetime(transaction_product_data['transaction_date'])
    start_date = pd.to_datetime('2021-01-01')
    end_date = pd.to_datetime('2021-12-31')

    filtered_data = transaction_product_data[(transaction_product_data['transaction_date'] >= start_date) & (transaction_product_data['transaction_date'] <= end_date) & (transaction_product_data['Store_outlet_id'] == store_id)]

    # Group the data by product ID and calculate the sum of quantities sold
    product_sales = filtered_data.groupby('product_id')['qty'].sum().sort_values(ascending=False)

    # Get the top 10 products with the highest sales
    high_demand_products = product_sales.head(10)

    # Prepare data for the bar chart
    product_ids = high_demand_products.index.to_list()
    product_names = [product_data[product_data['id'] == product_id]['name'].values[0] for product_id in product_ids]
    quantities = high_demand_products.values.tolist()

    return product_names, quantities
# Get high demand products for a specific store (example: store_id=2)
store_id = 4
product_name, quantities = product_with_high_demand_in_specific_time_period(transaction_product_data, store_id, product_data)
high_demand_insight = f"The top 10 high demand products in store {store_id} for the year 2021 are: " + ", ".join([f"{name} (Quantity: {qty})" for name, qty in zip(product_names, quantities)]) + "."

# Generate random expiry dates within a range
start_date = datetime.today()
end_date = start_date + timedelta(days=365)

# Add a new column for expiry_date
product_batch_data['expiry_date'] = [random.uniform(start_date, end_date) for _ in range(len(product_batch_data))]

def update_expiry_graph(product_batch_data,store_id):
    
    expiring_products_data = product_batch_data.copy()
    expiring_products_data['days_to_expiry'] = (expiring_products_data['expiry_date'] - datetime.today()).dt.days
    expiring_products_data = expiring_products_data[(expiring_products_data['days_to_expiry'] <= 2) & (expiring_products_data['store_outlet_id'] == store_id)]

    product_names_expiry = []
    days_to_expiry = []
    for _, row in expiring_products_data.iterrows():
        product_name = product_data[product_data['id'] == row['product_id']]['name'].values[0]
        if row['days_to_expiry'] >= 0:
            days_to_expiry.append(row['days_to_expiry'])
            product_names_expiry.append(product_name)


    return days_to_expiry,product_names_expiry

days_to_expiry,product_names_expiry=update_expiry_graph(product_batch_data,store_id)
expiring_products_insight = f"The products expiring within the next 2 days in store {store_id} are: " + ", ".join([f"{name} (Days to expiry: {days})" for name, days in zip(product_names_expiry, days_to_expiry)]) + "."

# **14. Products which are bought together

def product_bought_together(pair_df):

    # Prepare data for the bar chart
    product_names = []
    count=[]
    for i in range(10):
        product_names.append(f"{pair_df['Product 1'][i]} & {pair_df['Product 2'][i]}")
        count.append(pair_df['Co-occurrence Count'][i])
        
    # print(product_names,count)
    return product_names,count

product_names_together,counts=product_bought_together(pair_df)  
products_together_insight = "The top 10 products bought together are: " + ", ".join([f"{pair} (Count: {count})" for pair, count in zip(product_names_together, counts)]) + "."

def top5_customers_based_on_amount_by_store(transaction_data, transaction_product_data_1a,store_id):
    # Merge transaction and customer data
    merged_data = pd.merge(transaction_data, transaction_product_data_1a, on='transaction_id', how='left')
    merged_data=merged_data[merged_data['Store_outlet_id']==store_id]
    # Calculate the total amount purchased by each customer for each store
    customer_purchases = merged_data.groupby(['customer_id_y', 'Store_outlet_id'])['net_amount'].sum()

    # Get the top 5 customers for each store based on total amount purchased
    top_5_customers_by_store = customer_purchases.groupby('Store_outlet_id').nlargest(5)

    # Print the top 5 customers for each store
    print("Top 5 Customers by Store (Based on Amount Purchased):")
    for store_id, customer_purchases in top_5_customers_by_store.groupby('Store_outlet_id'): # group the series by store id
        print(f"\nStore ID: {store_id}")
        for customer_id, amount in customer_purchases.items(): # iterate over the multi-index series
            #customer_name = customer_data[customer_data['customer_id'] == customer_id]['customer_name'].values[0]
            print(f"- Customer Id: {customer_id[1]}, Total Amount Purchased: {amount:.2f}")

    top_5_customers_by_store = customer_purchases.groupby('Store_outlet_id').nlargest(5)
    store_130_customers = top_5_customers_by_store.loc[store_id]

    customer_names = []
    purchase_amounts = []

    for customer_id, amount in store_130_customers.items():
        # customer_name = customer_data[customer_data['customer_id'] == customer_id]['customer_name'].values[0]
        customer_names.append(str(customer_id[1]))
        purchase_amounts.append(amount)
    print(customer_names)
    return customer_names,purchase_amounts
customer_names,purchase_amount=top5_customers_based_on_amount_by_store(transaction_data, transaction_product_data,store_id)
top_customers_insight = f"The top 5 customers in store {store_id} based on the amount purchased are: " + ", ".join([f"Customer ID: {name} (Amount: {amount})" for name, amount in zip(customer_names, purchase_amount)]) + "."

# **3. Average customer traffic in store 2 monthly in the year 2022
def average_customer_traffic_in_specific_store_per_month(transaction_data,year,store_id):
    # Convert 'transaction_date' to datetime
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])

    # Filter data for 2022 and store 2
    transaction_data_2022_store2 = transaction_data[(transaction_data['transaction_date'].dt.year == year) & (transaction_data['store_outlet_id'] == store_id)]

    # Group data by month and count transactions
    monthly_traffic = transaction_data_2022_store2.groupby(pd.Grouper(key='transaction_date', freq='M')).size()

    # Calculate average customer traffic per month
    average_traffic_by_month = monthly_traffic  # No need to calculate the mean again

    # Convert 'transaction_date' to datetime
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])

    # Filter data for 2022 and store 2
    transaction_data_2022_store2 = transaction_data[(transaction_data['transaction_date'].dt.year == year) & (transaction_data['store_outlet_id'] == store_id)]

    # Group data by month and count transactions
    monthly_traffic = transaction_data_2022_store2.groupby(pd.Grouper(key='transaction_date', freq='M')).size()

    return monthly_traffic.index.strftime('%Y-%m'), monthly_traffic.values

monthly_traffic_index,monthly_traffic_value=average_customer_traffic_in_specific_store_per_month(transaction_data,2022,2)
customer_traffic_insight = "The average monthly customer traffic in store 2 for the year 2022 is: " + ", ".join([f"{month} (Traffic: {traffic})" for month, traffic in zip(monthly_traffic_index, monthly_traffic_value)]) + "."

def average_transaction_value_in_specific_store_in_year(transaction_data,year,store_id):
    # Convert 'transaction_date' to datetime
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])

    # Filter data for 2022 and store 2
    transaction_data_2022_store2 = transaction_data[(transaction_data['transaction_date'].dt.year == year) & (transaction_data['store_outlet_id'] == store_id)]

    # Group data by month and calculate average transaction value
    average_transaction_value_by_month = transaction_data_2022_store2.groupby(pd.Grouper(key='transaction_date', freq='M'))['net_amount'].mean()

    return average_transaction_value_by_month.index.strftime('%Y-%m'), average_transaction_value_by_month.values

average_transaction_value_by_month_index, average_transaction_value_by_month_values=average_transaction_value_in_specific_store_in_year(transaction_data,2022,2)
transaction_value_insight = "The average monthly transaction value in store 2 for the year 2022 is: " + ", ".join([f"{month} (Value: {value:.2f})" for month, value in zip(average_transaction_value_by_month_index, average_transaction_value_by_month_values)]) + "."

# Convert 'transaction_date' to datetime
transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])
transaction_product_data['transaction_date'] = pd.to_datetime(transaction_product_data['transaction_date'])

def predict_the_product_whos_qty_to_increased(transaction_product_data_1a, store_id):
    # Calculate the profit for each product in the specified store
    store_profit = transaction_product_data_1a[transaction_product_data_1a['Store_outlet_id'] == store_id].groupby('product_id')['profit'].sum()
    
    # Sort the products by profit in descending order
    sorted_products = store_profit.sort_values(ascending=False)
    
    # Select the top 10 products with the highest profit
    top_10_products = sorted_products.head(10)
        
    # Calculate the average quantity sold for each product in the specified store
    store_avg_qty = transaction_product_data_1a[transaction_product_data_1a['Store_outlet_id'] == store_id].groupby('product_id')['qty'].mean()
    
    # Merge the average quantity with the top 10 products by profit
    merged_data = pd.merge(top_10_products, store_avg_qty, left_index=True, right_index=True)
    
    # Sort the merged data by average quantity in ascending order
    merged_data = merged_data.sort_values(by='qty', ascending=True)
    
    # Select the bottom 5 products with the lowest average quantity
    bottom_5_products = merged_data.head(5)
    
    return bottom_5_products
    
# Convert 'transaction_date' to datetime
transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])

# Filter data for store 2
transaction_data_store2 = transaction_data[transaction_data['store_outlet_id'] == 96]

# Group data by month and calculate total sales
monthly_sales = transaction_data_store2.groupby(pd.Grouper(key='transaction_date', freq='M'))['net_amount'].sum()

# Split the data into training and test sets
train_data = monthly_sales[:'2023-12-31']
test_data = monthly_sales['2024-01-01':]

# Train the ARIMA model
# Define the order (p, d, q)
order = (5, 1, 0)  # Adjust the order based on ACF and PACF plots for better results
model = ARIMA(train_data, order=order)
model_fit = model.fit()

# Forecast sales for January to December 2024 (including test data period)
forecast_steps = len(pd.date_range(start='2024-01-01', end='2024-12-01', freq='M'))
forecast = model_fit.get_forecast(steps=forecast_steps)
forecast_dates = pd.date_range(start='2024-01-01', periods=forecast_steps, freq='M')
forecast_sales = forecast.predicted_mean

transaction_product_data['profit'] = (transaction_product_data['sales_price'] - transaction_product_data['rate']) * transaction_product_data['qty']
 # Get the product recommendations
bottom_5_products = predict_the_product_whos_qty_to_increased(transaction_product_data, store_id)
product_prediction_insight = "The top 5 products in store 4 whose quantity needs to be increased are: " + ", ".join([f"Product ID: {index} (Profit: {profit}, Average Quantity: {qty})" for index, (profit, qty) in bottom_5_products.iterrows()]) + "."

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define the main dashboard layout
def specific_page():
    return html.Div(
        style={
            'backgroundImage': 'url(https://wallpaperaccess.com/full/1624843.jpg)',
            'backgroundSize': 'cover',
            'padding': '20px'
        },
        children=[
            nav_bar(),
            html.H1(
                "Analysis on Individual Store",
                style={'textAlign': 'center', 'color': '#ffffff', 'backgroundColor': 'rgba(0, 0, 0, 0.5)', 'padding': '10px'}
            ),
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-around'},
                children=[
                    html.Div([
                        html.Label("Store ID:"),
                        dcc.Input(id='store-id-input', type='number', value=4),
                        html.Button(id='submit-button', n_clicks=0, children='Submit')
                    ]),
                ]
            ),
            html.Div(
                style={'display': 'flex','backgroundColor':'rgba(255, 0, 0, 0.5)'},
                children=[
                    html.H3("Prediction on Individual Store",style={'textAlign': 'left', 'color': '#ffffff', 'backgroundColor': 'rgba(0, 0, 0, 0.5)', 'padding': '10px'}),
                ]
            ),
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-around','margin': '0px 0','backgroundColor':'rgba(255, 0, 0, 0.5)'},
                children=[
                    dcc.Graph(
                        id='sale-forecast',
                        figure=go.Figure(
                            data=[
                                go.Scatter(
                                    x=forecast_dates,
                                    y=forecast_sales,
                                    mode='lines+markers',
                                    name='Forecasted Sales (2024)',
                                    line=dict(color='#1f77b4', width=2),
                                    marker=dict(size=6, color='#1f77b4')
                                )
                            ],
                            layout=go.Layout(
                                title=dict(text=f'Sales Forecast for Store {store_id}', font=dict(size=20)),
                                xaxis=dict(
                                    title='Month',
                                    gridcolor='rgba(200, 200, 200, 0.5)',
                                    showline=True,
                                    linewidth=1,
                                    linecolor='black',
                                    ticks='outside'
                                ),
                                yaxis=dict(
                                    title='Sales',
                                    gridcolor='rgba(200, 200, 200, 0.5)',
                                    showline=True,
                                    linewidth=1,
                                    linecolor='black',
                                    ticks='outside'
                                ),
                                legend=dict(x=0, y=1, bgcolor='rgba(255, 255, 255, 0.5)'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333', size=12),
                                margin=dict(l=50, r=20, t=70, b=50)
                            )
                        )
                    ),
                    dcc.Graph(
                        id='high-demand-products-store',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=[list(product_data[product_data['id']==id]['name'])[0] for id in bottom_5_products.index.to_list()],
                                    y=bottom_5_products['qty'],
                                    text=[f"Profit: {profit}" for profit in bottom_5_products['profit']],
                                    textposition='auto',
                                    name='Product Quantity',
                                    marker=dict(color='#ff7f0e')
                                )
                            ],
                            layout=go.Layout(
                                title=dict(text=f'Products to Increase Quantity for Store {store_id}', font=dict(size=20)),
                                xaxis=dict(
                                    title='Product',
                                    gridcolor='rgba(200, 200, 200, 0.5)',
                                    showline=True,
                                    linewidth=1,
                                    linecolor='black',
                                    ticks='outside'
                                ),
                                yaxis=dict(
                                    title='Average Quantity Sold',
                                    gridcolor='rgba(200, 200, 200, 0.5)',
                                    showline=True,
                                    linewidth=1,
                                    linecolor='black',
                                    ticks='outside'
                                ),
                                legend=dict(x=0, y=1, bgcolor='rgba(255, 255, 255, 0.5)'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333', size=12),
                                margin=dict(l=50, r=20, t=70, b=50)
                            )
                        )
                    ),
                ]
            ),
            html.Div(
                style={'display': 'flex','backgroundColor':'rgba(255, 0, 0, 0.5)'},
                children=[
                    html.H3("  ",style={'textAlign': 'left', 'color': '#ffffff', 'backgroundColor': 'rgba(0, 0, 0, 0.5)', 'padding': '10px'}),
                ]
            ),
            html.Div(
                style={'display': 'flex','backgroundColor':'rgba(0,255, 0, 0.5)'},
                children=[
                    html.H3("Analysis on Individual Store",style={'textAlign': 'left', 'color': '#ffffff', 'backgroundColor': 'rgba(0, 0, 0, 0.5)', 'padding': '10px'}),
                ]
            ),
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-around','margin': '0px 0','backgroundColor':'rgba(0,255, 0, 0.5)'},
                children=[
                    # Graph component to display high-demand products in a specific time period by store
                    dcc.Graph(
                        id='high-demand-products',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=quantities,
                                    y=product_name,
                                    orientation='h',
                                    text=quantities,
                                    textposition='outside',
                                    marker=dict(color=px.colors.sequential.Bluered)
                                )
                            ],
                            layout=go.Layout(
                                title=f'Top 10 High Demand Products in Store {store_id} (2021-01-01 to 2021-12-31)',
                                xaxis=dict(title='Quantity Sold'),
                                yaxis=dict(title='Product Name'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333')
                            )
                        )
                    ),
                    dcc.Graph(
                        id='Products-near-Expiry',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=days_to_expiry,
                                    y=product_names_expiry,
                                    orientation='h',
                                    text=days_to_expiry,
                                    textposition='outside',
                                    marker=dict(color='rgb(255,127,14)', line=dict(color='rgb(0,0,0)', width=1.5))
                                )
                            ],
                            layout=go.Layout(
                                title=f'Products Near Expiry in Store {store_id}',
                                xaxis=dict(title='Number of Days to Expiry'),
                                yaxis=dict(title='Product Name'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333')
                            )
                        )
                    ),
                ]
            ),
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-around','margin': '0px 0','backgroundColor':'rgba(0,255, 0, 0.5)'},
                children=[
                    dcc.Graph(
                        id='Market-basket',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=product_names,
                                    y=counts,
                                    orientation='v',
                                    text=counts,
                                    textposition='inside',
                                    marker=dict(color=px.colors.sequential.Purp)
                                )
                            ],
                            layout=go.Layout(
                                title=f'Market Basket Analysis',
                                xaxis=dict(title='Product Name'),
                                yaxis=dict(title='Number of Times Bought'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333')
                            )
                        )
                    ),
                    dcc.Graph(
                        id='top5_customer',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=customer_names,
                                    y=purchase_amount,
                                    orientation='v',
                                    text=purchase_amount,
                                    textposition='outside',
                                    marker=dict(color=px.colors.sequential.Magma)
                                )
                            ],
                            layout=go.Layout(
                                title=f'Top 5 Customers in Store {store_id}',
                                xaxis=dict(title='Customer Name'),
                                yaxis=dict(title='Amount'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333')
                            )
                        )
                    ),
                ]
            ),
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-around','margin': '0px 0','backgroundColor':'rgba(0,255, 0, 0.5)'},
                children=[
                    dcc.Graph(
                        id='avg_cust_traffic',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=monthly_traffic_index,
                                    y=monthly_traffic_value,
                                    orientation='v',
                                    text=monthly_traffic_value,
                                    textposition='outside',
                                    marker=dict(color=px.colors.sequential.BuPu)
                                )
                            ],
                            layout=go.Layout(
                                title=f'Average Customer Traffic in Store {store_id}',
                                xaxis=dict(title='Month'),
                                yaxis=dict(title='Number of Customers'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333')
                            )
                        )
                    ),
                    dcc.Graph(
                        id='avg_transaction_value',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=average_transaction_value_by_month_index,
                                    y=average_transaction_value_by_month_values,
                                    orientation='v',
                                    text=average_transaction_value_by_month_values,
                                    textposition='outside',
                                    marker=dict(color=px.colors.sequential.Aggrnyl)
                                )
                            ],
                            layout=go.Layout(
                                title=f'Average Transaction Value in Store {store_id}',
                                xaxis=dict(title='Month'),
                                yaxis=dict(title='Transaction Value'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333')
                            )
                        )
                    ),
                ]
            ),
            html.Button(id='generate-report', n_clicks=0, children='Generate Report'),
            html.Div(id='report-output')
        ]
    )

# # Callback to update the graphs based on the store ID input
# @app.callback(
#     [Output('sales-forecast', 'figure'),
#      Output('product-recommendations', 'figure'),
#      Output('predicted-qty', 'children')],
#     Input('submit-button', 'n_clicks'),
#     State('store-id-input', 'value')
# )

# def update_graphs(n_clicks, store_id):
#     if store_id is None:
#         return go.Figure(), go.Figure()

#     # Filter data for the given store
#     transaction_data_store = transaction_data[transaction_data['store_outlet_id'] == store_id]

#     # Group data by month and calculate total sales
#     monthly_sales = transaction_data_store.groupby(pd.Grouper(key='transaction_date', freq='M'))['net_amount'].sum()

#     # Split the data into training and test sets
#     train_data = monthly_sales[:'2023-12-31']
#     test_data = monthly_sales['2024-01-01':]

#     # Train the linear regression model
#     model = LinearRegression()
#     model.fit(train_data.index.dayofyear.values.reshape(-1, 1), train_data.values)

#     # Forecast sales for January to December 2024
#     forecast_dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
#     forecast_sales = model.predict(forecast_dates.dayofyear.values.reshape(-1, 1))

#     # Create the sales forecast plotly graph
#     sales_forecast_figure = {
#         'data': [
#             go.Scatter(
#                 x=train_data.index,
#                 y=train_data.values,
#                 mode='lines',
#                 name='Actual Sales (2022-2023)'
#             ),
#             go.Scatter(
#                 x=test_data.index,
#                 y=test_data.values,
#                 mode='lines',
#                 name='Actual Sales (2024)'
#             ),
#             go.Scatter(
#                 x=forecast_dates,
#                 y=forecast_sales,
#                 mode='lines',
#                 name='Forecasted Sales (2024)'
#             )
#         ],
#         'layout': go.Layout(
#             title=f'Actual and Forecasted Sales for Store {store_id} (2022-2024)',
#             xaxis={'title': 'Month'},
#             yaxis={'title': 'Sales'},
#             legend={'x': 0, 'y': 1}
#         )
#     }

#     # Get the product recommendations
#     bottom_5_products = predict_the_product_whos_qty_to_increased(transaction_product_data, store_id)

#     # Create the product recommendations plotly graph
#     product_recommendations_figure = {
#         'data': [
#             go.Bar(
#                 x=[list(product_data[product_data['product_id']==id]['name'])[0] for id in bottom_5_products.index.to_list()],
#                 y=bottom_5_products['qty'],
#                 text=[f"Profit: {profit}" for profit in bottom_5_products['profit']],
#                 name='Product Quantity'
#             )
#         ],
#         'layout': go.Layout(
#             title=f'Products to Increase Quantity for Store {store_id}',
#             xaxis={'title': 'Product'},
#             yaxis={'title': 'Average Quantity Sold'},
#             legend={'x': 0, 'y': 1}
#         )
#     }

#     # Predict the quantity for product with id=29 for June 2024
#     predicted_qty = predict_qty_of_product(transaction_product_data_1a, product_data, store_id, 29, '2024-06-01')
#     predicted_qty_text = f"Predicted quantity for product 29 in store {store_id} for June 2024: {predicted_qty:.2f}"

#     return sales_forecast_figure, product_recommendations_figure, predicted_qty_text
    
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

# Callback to update the graphs based on the store ID input
@app.callback(
    [Output('sales-forecast', 'figure'),
     Output('product-recommendations', 'figure'),
     Output('predicted-qty', 'children')],
    Input('submit-button', 'n_clicks'),

)

def update_graphs(n_clicks, store_id):
    if store_id is None:
        return go.Figure(), go.Figure()

    # Filter data for the given store
    transaction_data_store = transaction_data[transaction_data['store_outlet_id'] == store_id]

    # Group data by month and calculate total sales
    monthly_sales = transaction_data_store.groupby(pd.Grouper(key='transaction_date', freq='M'))['net_amount'].sum()

    # Split the data into training and test sets
    train_data = monthly_sales[:'2023-12-31']
    test_data = monthly_sales['2024-01-01':]

    # Train the linear regression model
    model = LinearRegression()
    model.fit(train_data.index.dayofyear.values.reshape(-1, 1), train_data.values)

    # Forecast sales for January to December 2024
    forecast_dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    forecast_sales = model.predict(forecast_dates.dayofyear.values.reshape(-1, 1))

    # Create the sales forecast plotly graph
    sales_forecast_figure = {
        'data': [
            go.Scatter(
                x=train_data.index,
                y=train_data.values,
                mode='lines',
                name='Actual Sales (2022-2023)'
            ),
            go.Scatter(
                x=test_data.index,
                y=test_data.values,
                mode='lines',
                name='Actual Sales (2024)'
            ),
            go.Scatter(
                x=forecast_dates,
                y=forecast_sales,
                mode='lines',
                name='Forecasted Sales (2024)'
            )
        ],
        'layout': go.Layout(
            title=f'Actual and Forecasted Sales for Store {store_id} (2022-2024)',
            xaxis={'title': 'Month'},
            yaxis={'title': 'Sales'},
            legend={'x': 0, 'y': 1}
        )
    }

    # Get the product recommendations
    bottom_5_products = predict_the_product_whos_qty_to_increased(transaction_product_data, store_id)

    # Create the product recommendations plotly graph
    product_recommendations_figure = {
        'data': [
            go.Bar(
                x=[list(product_data[product_data['product_id']==id]['name'])[0] for id in bottom_5_products.index.to_list()],
                y=bottom_5_products['qty'],
                text=[f"Profit: {profit}" for profit in bottom_5_products['profit']],
                name='Product Quantity'
            )
        ],
        'layout': go.Layout(
            title=f'Products to Increase Quantity for Store {store_id}',
            xaxis={'title': 'Product'},
            yaxis={'title': 'Average Quantity Sold'},
            legend={'x': 0, 'y': 1}
        )
    }

    # Predict the quantity for product with id=29 for June 2024
    predicted_qty = predict_qty_of_product(transaction_product_data_1a, product_data, store_id, 29, '2024-06-01')
    predicted_qty_text = f"Predicted quantity for product 29 in store {store_id} for June 2024: {predicted_qty:.2f}"

    return sales_forecast_figure, product_recommendations_figure, predicted_qty_text
    
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

# Callback to generate and display the report
@app.callback(
    Output('report-output', 'children'),
    Input('generate-report', 'n_clicks')
)
def update_report(n_clicks):
    if n_clicks > 0:
        report_text = f"""
        {high_demand_insight}
        {expiring_products_insight}
        {products_together_insight}
        {top_customers_insight}
        {customer_traffic_insight}
        {transaction_value_insight}
        {product_prediction_insight}
        """
        return html.Div([
            html.H3("Generated Report"),
            html.P(report_text)
        ])
    return html.Div()
# app.css.append_css({"external_url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"})
# app.css.append_css({"external_url": "data:text/css," + styles})

if __name__ == '__main__':
    app.run_server(debug=True)