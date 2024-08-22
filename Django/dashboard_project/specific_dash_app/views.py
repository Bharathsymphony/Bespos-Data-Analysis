from django.shortcuts import render
import pandas as pd
from .data_analysis.analysis import expiry_graph,product_with_high_demand_in_specific_time_period,product_bought_together,top5_customers_based_on_amount_by_store,average_customer_traffic_in_specific_store_per_month,average_transaction_value_in_specific_store_in_year,predict_the_product_whos_qty_to_increased
from datetime import datetime, timedelta
import random
from django.http import JsonResponse

def get_store_data(request,store_id):
    transaction_data = pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/transaction_data.csv')
    transaction_product_data = pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/transaction_product_data_1a.csv')
    product_data = pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/PRODUCT.csv')
    product_batch_data= pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/PRODUCT_BATCH_data.csv')
    pair_df=pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/pairs_df.csv')

    transaction_data.rename(columns={'id': 'transaction_id'}, inplace=True)
    store_ids=sorted(transaction_data['store_outlet_id'].unique())
    # Generate random expiry dates within a range
    start_date = datetime.today()
    end_date = start_date + timedelta(days=365)

    # Add a new column for expiry_date
    product_batch_data['expiry_date'] = [random.uniform(start_date, end_date) for _ in range(len(product_batch_data))]

    transaction_product_data['profit'] = (transaction_product_data['sales_price'] - transaction_product_data['rate']) * transaction_product_data['qty']
    year=2022
    product_names_demand, quantities=product_with_high_demand_in_specific_time_period(transaction_product_data, store_id, product_data)
    days_to_expiry,product_names_expiry=expiry_graph(product_batch_data,store_id)
    product_names,count=product_bought_together(pair_df)
    customer_names,purchase_amounts=top5_customers_based_on_amount_by_store(transaction_data, transaction_product_data,store_id)
    month,traffic=average_customer_traffic_in_specific_store_per_month(transaction_data,year,store_id)
    time_period,transaction_value=average_transaction_value_in_specific_store_in_year(transaction_data,year,store_id)
    bottom_5_products=predict_the_product_whos_qty_to_increased(transaction_product_data, store_id)

    context = {
        'st_id':store_id,
        'store_ids':store_ids,
        'products_with_high_demand_in_specific_time_period': {'product_names_demand': product_names_demand, 'quantities': quantities},
        'products_to_expiry': {'days_to_expiry': days_to_expiry, 'product_names_expiry': product_names_expiry},
        'product_bought_together': {'product_names': product_names, 'count': count},
        'top_customers_based_on_amount_by_store': {'customer_names': customer_names, 'purchase_amounts': purchase_amounts},
        'average_customer_traffic_in_specific_store_per_month': {'month': month, 'traffic': traffic},
        'average_transaction_value_in_specific_store_in_year': {'time_period': time_period, 'transaction_value': transaction_value},
        'bottom_5_products': bottom_5_products.to_dict(orient='list'),
    }

    return render(request, 'specific_dash_app/dashboard.html', context)