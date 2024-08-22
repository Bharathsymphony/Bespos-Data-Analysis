from django.shortcuts import render
import pandas as pd
from .data_analysis.analysis import run_analysis, product_with_high_demand_in_specific_time_period, sales_growth_in_specific_time_period, average_customer_traffic_in_a_year, average_transaction_value_by_store_in_specific_month, average_basket_size_specific_month, profit_in_each_store_by_year
import json

def dashboard_view(request):
    # Load your datasets
    transaction_data = pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/transaction_data.csv')
    transaction_product_data = pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/transaction_product_data_1a.csv')
    product_data = pd.read_csv('C:/Users/bhara/Desktop/Bharath/Sesame technologies/Django/dashboard_project/dashboard_app/PRODUCT.csv')
    # Run analyses 
    top_stores, average_transaction_value_by_store = run_analysis()

    store_id = 2
    product_names, quantities = product_with_high_demand_in_specific_time_period(transaction_product_data, store_id, product_data)

    growth_data = sales_growth_in_specific_time_period(transaction_data)

    initial_average_traffic_data = average_customer_traffic_in_a_year(transaction_data, 2023)

    average_transaction_value_data, month_name = average_transaction_value_by_store_in_specific_month(transaction_data, 2022, 4)

    average_basket_size_data, basket_month_name = average_basket_size_specific_month(transaction_data, transaction_product_data, 2022, 2)

    profit_data_2022 = profit_in_each_store_by_year(transaction_product_data, 2022)
    
    context = {
        'top_stores': top_stores.to_dict(orient='list'),
        'average_transaction_value_by_store': average_transaction_value_by_store.to_dict(orient='list'),
        'high_demand_products': {'names': product_names, 'quantities': quantities},
        'sales_growth_data': growth_data.to_dict(orient='list'),
        'average_traffic_data': initial_average_traffic_data.to_dict(orient='list'),
        'average_transaction_value_data': average_transaction_value_data.to_dict(orient='list'),
        'average_basket_size_data': average_basket_size_data.to_dict(orient='list'),
        'profit_data': profit_data_2022.to_dict(orient='list'),
        'month_name': month_name,
        'basket_month_name': basket_month_name,
    }

    return render(request, 'dashboard_app/dashboard.html', context)
