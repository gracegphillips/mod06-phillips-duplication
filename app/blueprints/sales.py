# In sales.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from app.functions import calculate_total_sales_by_region, analyze_monthly_sales_trends, identify_top_performing_region



sales = Blueprint('sales', __name__)

@sales.route('/show_sales')
def show_sales():
    connection = get_db()
    query = "SELECT * FROM sales_data"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result)
    df['Actions'] = df['sale_id'].apply(lambda id:
      f'<a href="{url_for("sales.edit_sales_data", sale_id=id)}" class="btn btn-sm btn-info">Edit</a> '
      f'<form action="{url_for("sales.delete_sales_data", sale_id=id)}" method="post" style="display:inline;">'
      f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
      )
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, header=False, escape=False)
    rows_only = table_html.split('<tbody>')[1].split('</tbody>')[0]

    return render_template("sales_data.html", table=rows_only)

@sales.route('/add_sales_data', methods=['GET', 'POST'])
def add_sales_data():
    if request.method == 'POST':
        monthly_amount = request.form['monthly_amount']
        date = request.form['date']
        region = request.form['region']

        connection = get_db()
        query = "INSERT INTO sales_data (monthly_amount, date, region) VALUES (%s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (monthly_amount, date, region))
        connection.commit()
        flash("New sales data added successfully!", "success")
        return redirect(url_for('sales.show_sales'))

    return render_template("add_sales_data.html")

@sales.route('/edit_sales_data/<int:sale_id>', methods=['GET', 'POST'])
def edit_sales_data(sale_id):
    connection = get_db()
    if request.method == 'POST':
        monthly_amount = request.form['monthly_amount']
        date = request.form['date']
        region = request.form['region']

        query = "UPDATE sales_data SET monthly_amount = %s, date = %s, region = %s WHERE sale_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (monthly_amount, date, region, sale_id))
        connection.commit()
        flash("Sales data updated successfully!", "success")
        return redirect(url_for('sales.show_sales'))

    query = "SELECT * FROM sales_data WHERE sale_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (sale_id,))
        sales_data = cursor.fetchone()

    return render_template("edit_sales_data.html", sales_data=sales_data)

@sales.route('/delete_sales_data/<int:sale_id>', methods=['POST'])
def delete_sales_data(sale_id):
    connection = get_db()
    query = "DELETE FROM sales_data WHERE sale_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (sale_id,))
    connection.commit()
    flash("Sales data deleted successfully!", "success")
    return redirect(url_for('sales.show_sales'))# In sales.py



#####for regions table


@sales.route('/show_regions')
def show_regions():
    connection = get_db()
    query = "SELECT * FROM regions"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result)
    df['Actions'] = df['region_id'].apply(lambda id:
      f'<a href="{url_for("sales.edit_region", region_id=id)}" class="btn btn-sm btn-info">Edit</a> '
      f'<form action="{url_for("sales.delete_region", region_id=id)}" method="post" style="display:inline;">'
      f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
      )
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, header=False, escape=False)
    rows_only = table_html.split('<tbody>')[1].split('</tbody>')[0]

    return render_template("regions.html", table=rows_only)

@sales.route('/add_region', methods=['GET', 'POST'])
def add_region():
    if request.method == 'POST':
        region_name = request.form['region_name']

        connection = get_db()
        query = "INSERT INTO regions (region_name) VALUES (%s)"
        with connection.cursor() as cursor:
            cursor.execute(query, (region_name,))
        connection.commit()
        flash("New region added successfully!", "success")
        return redirect(url_for('regions.show_regions'))

    return render_template("add_region.html")

@sales.route('/edit_region/<int:region_id>', methods=['GET', 'POST'])
def edit_region(region_id):
    connection = get_db()
    if request.method == 'POST':
        region_name = request.form['region_name']

        query = "UPDATE regions SET region_name = %s WHERE region_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (region_name, region_id))
        connection.commit()
        flash("Region updated successfully!", "success")
        return redirect(url_for('regions.show_regions'))

    query = "SELECT * FROM regions WHERE region_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (region_id,))
        region = cursor.fetchone()

    return render_template("edit_region.html", region=region)

@sales.route('/delete_region/<int:region_id>', methods=['POST'])
def delete_region(region_id):
    connection = get_db()
    query = "DELETE FROM regions WHERE region_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (region_id,))
    connection.commit()
    flash("Region deleted successfully!", "success")
    return redirect(url_for('regions.show_regions'))





# Reports route
@sales.route('/reports')
def show_reports():
    connection = get_db()

    # Total Sales by Region
    df_total_sales_by_region = calculate_total_sales_by_region(connection)
    total_sales_by_region_html = df_total_sales_by_region.to_html(classes='dataframe table table-striped table-bordered', index=False, escape=False)

    # Monthly Sales Trend
    df_monthly_sales_trend = analyze_monthly_sales_trends(connection)
    monthly_sales_trend_html = df_monthly_sales_trend.to_html(classes='dataframe table table-striped table-bordered', index=False, escape=False)

    # Top-Performing Region
    top_performing_region = identify_top_performing_region(df_total_sales_by_region)
    top_performing_region_html = top_performing_region.to_frame().T.to_html(classes='dataframe table table-striped table-bordered', index=False, escape=False)

    return render_template("reports.html", total_sales_by_region=total_sales_by_region_html, monthly_sales_trend=monthly_sales_trend_html, top_performing_region=top_performing_region_html)




# Visualization route
@sales.route('/visualization')
def show_visualization():
    connection = get_db()

    # Fetch sales data
    query = "SELECT region_id, SUM(amount) as total_sales FROM sales_data GROUP BY region_id"
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result)

    # Generate bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(df['region_id'], df['total_sales'], color='skyblue')
    plt.xlabel('Region ID')
    plt.ylabel('Total Sales')
    plt.title('Total Sales by Region')

    # Save the chart to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    # Convert the BytesIO object to a base64 string
    chart_base64 = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template("visualization.html", chart_base64=chart_base64)
