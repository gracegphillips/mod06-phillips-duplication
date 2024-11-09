# In functions.py

import pandas as pd


def calculate_total_sales_by_region(connection):
    query = "SELECT region_id, SUM(amount) as total_sales FROM sales_data GROUP BY region_id"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result)
    return df

def analyze_monthly_sales_trends(connection):
    query = "SELECT DATE_FORMAT(sale_date, '%Y-%m') as month, SUM(amount) as total_sales FROM sales_data GROUP BY month ORDER BY month"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result)
    return df

def identify_top_performing_region(df_total_sales_by_region):
    top_performing_region = df_total_sales_by_region.loc[df_total_sales_by_region['total_sales'].idxmax()]
    return top_performing_region
