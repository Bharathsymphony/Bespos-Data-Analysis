import pandas as pd
from datetime import datetime, timedelta
import random

product_data = pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/PRODUCT.csv')
product_batch_data= pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/PRODUCT_BATCH_data.csv')


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
    product_names_demand = [product_data[product_data['id'] == product_id]['name'].values[0] for product_id in product_ids]
    quantities = high_demand_products.values.tolist()

    return product_names_demand, quantities

def expiry_graph(product_batch_data,store_id):
    
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

def product_bought_together(pair_df):

    # Prepare data for the bar chart
    product_names = []
    count=[]
    for i in range(10):
        product_names.append(f"{pair_df['Product 1'][i]} & {pair_df['Product 2'][i]}")
        count.append(pair_df['Co-occurrence Count'][i])
        
    # print(product_names,count)
    return product_names,count

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

def average_transaction_value_in_specific_store_in_year(transaction_data,year,store_id):
    # Convert 'transaction_date' to datetime
    transaction_data['transaction_date'] = pd.to_datetime(transaction_data['transaction_date'])

    # Filter data for 2022 and store 2
    transaction_data_2022_store2 = transaction_data[(transaction_data['transaction_date'].dt.year == year) & (transaction_data['store_outlet_id'] == store_id)]

    # Group data by month and calculate average transaction value
    average_transaction_value_by_month = transaction_data_2022_store2.groupby(pd.Grouper(key='transaction_date', freq='M'))['net_amount'].mean()

    return average_transaction_value_by_month.index.strftime('%Y-%m'),average_transaction_value_by_month.values

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