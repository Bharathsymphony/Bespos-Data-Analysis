import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from nav import nav_bar
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA

# Load your datasets
transaction_data = pd.read_csv('Dataset/TRANSACTION.csv')
transaction_product_data = pd.read_csv('Dataset/transaction_product_data_1a.csv')
product_data = pd.read_csv('Dataset/PRODUCT.csv')
product_batch_data= pd.read_csv('Dataset/PRODUCT_BATCH_data.csv')
pair_df=pd.read_csv('Dataset/pairs_df.csv')

transaction_data.rename(columns={'id': 'transaction_id'}, inplace=True)

# Function to calculate high-demand products in a specific time period by store
def product_with_high_demand_in_specific_time_period(transaction_product_data, store_id, product_data):
    transaction_product_data['transaction_date'] = pd.to_datetime(transaction_product_data['transaction_date'])
    start_date = pd.to_datetime('2021-01-01')
    end_date = pd.to_datetime('2021-12-31')

    filtered_data = transaction_product_data[
        (transaction_product_data['transaction_date'] >= start_date) &
        (transaction_product_data['transaction_date'] <= end_date) &
        (transaction_product_data['Store_outlet_id'] == store_id)
    ]

    product_sales = filtered_data.groupby('product_id')['qty'].sum().sort_values(ascending=False)
    high_demand_products = product_sales.head(10)

    product_ids = high_demand_products.index.to_list()
    product_names = [product_data[product_data['id'] == product_id]['name'].values[0] for product_id in product_ids]
    quantities = high_demand_products.values.tolist()

    return product_names, quantities

# Generate random expiry dates within a range
start_date = datetime.today()
end_date = start_date + timedelta(days=365)
product_batch_data['expiry_date'] = [random.uniform(start_date, end_date) for _ in range(len(product_batch_data))]

def update_expiry_graph(product_batch_data, store_id):
    expiring_products_data = product_batch_data.copy()
    expiring_products_data['days_to_expiry'] = (expiring_products_data['expiry_date'] - datetime.today()).dt.days
    expiring_products_data = expiring_products_data[
        (expiring_products_data['days_to_expiry'] <= 2) &
        (expiring_products_data['store_outlet_id'] == store_id)
    ]

    product_names_expiry = []
    days_to_expiry = []
    for _, row in expiring_products_data.iterrows():
        product_name = product_data[product_data['id'] == row['product_id']]['name'].values[0]
        if row['days_to_expiry'] >= 0:
            days_to_expiry.append(row['days_to_expiry'])
            product_names_expiry.append(product_name)

    return days_to_expiry, product_names_expiry

def product_bought_together(pair_df):
    product_names = [f"{pair_df['Product 1'][i]} & {pair_df['Product 2'][i]}" for i in range(10)]
    count = pair_df['Co-occurrence Count'][:10].tolist()
    return product_names, count

def top5_customers_based_on_amount_by_store(transaction_data, transaction_product_data, store_id):

    # Merge transaction and customer data
    merged_data = pd.merge(transaction_data, transaction_product_data, on='transaction_id', how='left')
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

    return customer_names, purchase_amounts

def average_customer_traffic_in_specific_store_per_month(transaction_data, year, store_id):
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])
    transaction_data_filtered = transaction_data[
        (transaction_data['transaction_date'].dt.year == year) &
        (transaction_data['store_outlet_id'] == store_id)
    ]

    monthly_traffic = transaction_data_filtered.groupby(pd.Grouper(key='transaction_date', freq='M')).size()
    return monthly_traffic.index.strftime('%Y-%m'), monthly_traffic.values

def average_transaction_value_in_specific_store_in_year(transaction_data, year, store_id):
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])
    transaction_data_filtered = transaction_data[
        (transaction_data['transaction_date'].dt.year == year) &
        (transaction_data['store_outlet_id'] == store_id)
    ]

    avg_transaction_value_by_month = transaction_data_filtered.groupby(pd.Grouper(key='transaction_date', freq='M'))['net_amount'].mean()
    return avg_transaction_value_by_month.index.strftime('%Y-%m'), avg_transaction_value_by_month.values

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

def sales_forcast(transaction_data,store_id):    
    # Convert 'transaction_date' to datetime
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])
    
    # Filter data for store 2
    transaction_data_store2 = transaction_data[transaction_data['store_outlet_id'] == store_id]
    
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
    return forecast_dates,forecast_sales

transaction_product_data['profit'] = (transaction_product_data['sales_price'] - transaction_product_data['rate']) * transaction_product_data['qty']
 # Get the product recommendations
bottom_5_products = predict_the_product_whos_qty_to_increased(transaction_product_data, 2)

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div(
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
            style={'display': 'flex', 'justifyContent': 'center', 'margin': '20px'},
            children=[
                dcc.Dropdown(
                    id='store-id-dropdown',
                    options=[{'label': f'Store {i}', 'value': i} for i in sorted(transaction_product_data['Store_outlet_id'].unique())],
                    value=2,
                    placeholder="Select a store"
                ),
            ]
        ),
        html.Div(id='dashboard-content')
    ]
)

@app.callback(
    Output('dashboard-content', 'children'),
    [Input('store-id-dropdown', 'value')]
)
def update_dashboard(store_id):
    product_names, quantities = product_with_high_demand_in_specific_time_period(transaction_product_data, store_id, product_data)
    days_to_expiry, product_names_expiry = update_expiry_graph(product_batch_data, store_id)
    product_names_bought_together, counts = product_bought_together(pair_df)
    customer_names, purchase_amounts = top5_customers_based_on_amount_by_store(transaction_data, transaction_product_data, store_id)
    monthly_traffic_index, monthly_traffic_value = average_customer_traffic_in_specific_store_per_month(transaction_data, 2022, store_id)
    avg_transaction_value_by_month_index, avg_transaction_value_by_month_values = average_transaction_value_in_specific_store_in_year(transaction_data, 2022, store_id)
    bottom_5_products = predict_the_product_whos_qty_to_increased(transaction_product_data, store_id)
    forecast_dates,forecast_sales=sales_forcast(transaction_data,store_id)
    return html.Div(
        children=[
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
                                    # text=[f"Profit: {profit}" for profit in bottom_5_products['profit']],
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
                style={'display': 'flex', 'justifyContent': 'space-around','margin': '20px 0'},
                children=[
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
                        id='products-near-expiry',
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
                style={'display': 'flex', 'justifyContent': 'space-around'},
                children=[
                    dcc.Graph(
                        id='market-basket',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=counts,
                                    y=product_names_bought_together,
                                    orientation='h',
                                    text=counts,
                                    textposition='outside',
                                    marker=dict(color=px.colors.sequential.Oryel)
                                )
                            ],
                            layout=go.Layout(
                                title='Top 10 Product Pairs Bought Together',
                                xaxis=dict(title='Co-occurrence Count'),
                                yaxis=dict(title='Product Pair'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333')
                            )
                        )
                    ),
                    dcc.Graph(
                        id='top-customers',
                        figure=go.Figure(
                            data=[
                                go.Bar(
                                    x=purchase_amounts,
                                    y=customer_names,
                                    orientation='h',
                                    text=purchase_amounts,
                                    textposition='outside',
                                    marker=dict(color=px.colors.sequential.Emrld)
                                )
                            ],
                            layout=go.Layout(
                                title=f'Top 5 Customers in Store {store_id}',
                                xaxis=dict(title='Purchase Amount'),
                                yaxis=dict(title='Customer ID'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333')
                            )
                        )
                    ),
                ]
            ),
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-around'},
                children=[
                    dcc.Graph(
                        id='monthly-traffic',
                        figure=go.Figure(
                            data=[
                                go.Scatter(
                                    x=monthly_traffic_index,
                                    y=monthly_traffic_value,
                                    mode='lines+markers',
                                    marker=dict(color='rgba(31, 119, 180, 0.6)', size=10),
                                    line=dict(color='rgba(31, 119, 180, 0.8)', width=2)
                                )
                            ],
                            layout=go.Layout(
                                title=f'Average Customer Traffic per Month in Store {store_id} (2022)',
                                xaxis=dict(title='Month'),
                                yaxis=dict(title='Average Customer Traffic'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333')
                            )
                        )
                    ),
                    dcc.Graph(
                        id='average-transaction-value',
                        figure=go.Figure(
                            data=[
                                go.Scatter(
                                    x=avg_transaction_value_by_month_index,
                                    y=avg_transaction_value_by_month_values,
                                    mode='lines+markers',
                                    marker=dict(color='rgba(255, 127, 14, 0.6)', size=10),
                                    line=dict(color='rgba(255, 127, 14, 0.8)', width=2)
                                )
                            ],
                            layout=go.Layout(
                                title=f'Average Transaction Value per Month in Store {store_id} (2022)',
                                xaxis=dict(title='Month'),
                                yaxis=dict(title='Average Transaction Value'),
                                plot_bgcolor='rgba(255, 255, 255, 0.8)',
                                paper_bgcolor='rgba(255, 255, 255, 0.8)',
                                font=dict(color='#333')
                            )
                        )
                    )
                ]
            )
        ]
    )

# Callback to update the graphs based on the store ID input
@app.callback(
    [Output('sales-forecast', 'figure'),
     Output('product-recommendations', 'figure'),
     Output('predicted-qty', 'children')],
    Input('submit-button', 'n_clicks'),
    State('store-id-input', 'value')
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
    
if __name__ == '__main__':
    app.run_server(debug=True)
