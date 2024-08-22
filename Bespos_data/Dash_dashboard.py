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

# Load your datasets
transaction_data = pd.read_csv('Dataset/TRANSACTION.csv')
transaction_product_data = pd.read_csv('Dataset/transaction_product_data_1a.csv')
product_data = pd.read_csv('Dataset/PRODUCT.csv')
product_batch_data= pd.read_csv('Dataset/PRODUCT_BATCH_data.csv')

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


