import pandas as pd

def run_analysis():
    # Load your datasets
    transaction_data = pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/transaction_data.csv')
    transaction_product_data = pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/transaction_product_data_1a.csv')
    product_data = pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/PRODUCT.csv')

    # Rename 'id' column to 'transaction_id' in transaction_data for clarity
    transaction_data.rename(columns={'id': 'transaction_id'}, inplace=True)

    # Calculate the number of repeat customers for each store
    repeat_customers_by_store = transaction_data.groupby('store_outlet_id')['customer_id'].nunique()

    # Sort stores by the number of repeat customers in descending order and get the top 10
    top_stores_by_repeat_customers = repeat_customers_by_store.sort_values(ascending=False).head(10).reset_index()
    top_stores_by_repeat_customers.columns = ['Store_ID', 'Repeat_Customers']
    top_stores_by_repeat_customers['Store_ID'] = top_stores_by_repeat_customers['Store_ID'].astype(str)

    # Filter out transactions with non-positive net amounts
    transaction_data = transaction_data[transaction_data['net_amount'] > 0]

    # Calculate the average transaction value for each store
    average_transaction_value_by_store = transaction_data.groupby('store_outlet_id')['net_amount'].mean().reset_index()
    average_transaction_value_by_store.columns = ['Store_ID', 'Average_Transaction_Value']
    average_transaction_value_by_store['Store_ID'] = average_transaction_value_by_store['Store_ID'].astype(str)

    return top_stores_by_repeat_customers, average_transaction_value_by_store

def product_with_high_demand_in_specific_time_period(transaction_product_data, store_id, product_data):
    # Convert 'transaction_date' to datetime format
    transaction_product_data['transaction_date'] = pd.to_datetime(transaction_product_data['transaction_date'])
    
    # Define the time period for the analysis
    start_date = pd.to_datetime('2021-01-01')
    end_date = pd.to_datetime('2021-12-31')

    # Filter transactions for the specific store and time period
    filtered_data = transaction_product_data[(transaction_product_data['transaction_date'] >= start_date) & (transaction_product_data['transaction_date'] <= end_date) & (transaction_product_data['Store_outlet_id'] == store_id)]
    
    # Calculate the total quantity sold for each product and sort in descending order
    product_sales = filtered_data.groupby('product_id')['qty'].sum().sort_values(ascending=False)

    # Get the top 10 products with the highest demand
    high_demand_products = product_sales.head(10)
    product_ids = high_demand_products.index.to_list()
    
    # Retrieve product names and corresponding quantities sold
    product_names = [product_data[product_data['id'] == product_id]['name'].values[0] for product_id in product_ids]
    quantities = high_demand_products.values.tolist()

    return product_names, quantities

def sales_growth_in_specific_time_period(transaction_data):
    # Define the current time period for the analysis
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    
    # Filter transactions for the specified time period
    filtered_data = transaction_data[(transaction_data['transaction_date'] >= start_date) & (transaction_data['transaction_date'] <= end_date)]
    store_sales = filtered_data.groupby('store_outlet_id')['net_amount'].sum()

    # Define the previous time period for comparison
    previous_start_date = '2022-01-01'
    previous_end_date = '2022-12-31'
    previous_filtered_data = transaction_data[(transaction_data['transaction_date'] >= previous_start_date) & (transaction_data['transaction_date'] <= previous_end_date)]
    previous_store_sales = previous_filtered_data.groupby('store_outlet_id')['net_amount'].sum()

    # Calculate sales growth as a percentage change from the previous period
    growth_by_store = (store_sales - previous_store_sales) / previous_store_sales * 100
    growth_df = pd.DataFrame({
        'Store_ID': growth_by_store.index,
        'Sales_Growth': growth_by_store.values
    })

    return growth_df

def average_customer_traffic_in_a_year(transaction_data, year):
    # Convert 'transaction_date' to datetime format
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])
    
    # Filter transactions for the specified year
    transaction_data_year = transaction_data[transaction_data['transaction_date'].dt.year == year]
    
    # Group by store and month to calculate the number of transactions
    grouped_data = transaction_data_year.groupby(['store_outlet_id', pd.Grouper(key='transaction_date', freq='M')]).size()

    # Calculate the average traffic per store
    average_traffic_by_store = grouped_data.groupby(level=0).mean().reset_index()
    average_traffic_by_store.columns = ['Store_ID', 'Average_Traffic']

    return average_traffic_by_store

def average_transaction_value_by_store_in_specific_month(transaction_data, year, month):
    # Convert 'transaction_date' to datetime format
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])
    
    # Filter transactions for the specified year and month
    transaction_data_filtered = transaction_data[(transaction_data['transaction_date'].dt.year == year) & (transaction_data['transaction_date'].dt.month == month)]

    # If no transactions are found for the specified period, return empty DataFrame and None
    if transaction_data_filtered.empty:
        return pd.DataFrame(), None

    # Calculate the average transaction value for each store in the specified month
    average_transaction_value_by_store = transaction_data_filtered.groupby('store_outlet_id')['net_amount'].mean().reset_index()
    average_transaction_value_by_store.columns = ['Store_ID', 'Average_Transaction_Value']

    return average_transaction_value_by_store, pd.to_datetime(f'{year}-{month}-01').strftime('%B')

def average_basket_size_specific_month(transaction_data, transaction_product_data, year, month):
    # Rename 'id' column to 'transaction_id' in transaction_data for consistency
    transaction_data.rename(columns={'id': 'transaction_id'}, inplace=True)

    # Convert 'transaction_date' to datetime format
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])
    
    # Filter transactions for the specified year and month
    transaction_data_filtered = transaction_data[(transaction_data['transaction_date'].dt.year == year) & (transaction_data['transaction_date'].dt.month == month)]

    # If no transactions are found for the specified period, return empty DataFrame and None
    if transaction_data_filtered.empty:
        return pd.DataFrame(), None

    # Merge transaction and transaction product data to calculate basket size
    transaction_product_datas = pd.merge(transaction_data_filtered, transaction_product_data, on='transaction_id', how='left')
    
    # Calculate the average number of items per transaction for each store
    average_items_per_transaction = transaction_product_datas.groupby('store_outlet_id')['total_qty'].mean().reset_index()
    average_items_per_transaction.columns = ['Store_ID', 'Average_Items_per_Transaction']

    return average_items_per_transaction, pd.to_datetime(f'{year}-{month}-01').strftime('%B')

def profit_in_each_store_by_year(transaction_product, year):
    # Convert 'transaction_date' to datetime format
    transaction_product['transaction_date'] = pd.to_datetime(transaction_product['transaction_date'])
    
    # Filter transactions for the specified year
    transaction_data_filtered = transaction_product[transaction_product['transaction_date'].dt.year == year]
    
    # Calculate profit for each transaction as (sales_price - rate) * quantity
    transaction_data_filtered['profit'] = (transaction_data_filtered['sales_price'] - transaction_data_filtered['rate']) * transaction_data_filtered['qty']
    
    # Sum profits by store to calculate the total profit per store
    profit_by_store = transaction_data_filtered.groupby('Store_outlet_id')['profit'].sum().reset_index()
    profit_by_store.columns = ['Store_ID', 'Profit']

    return profit_by_store
