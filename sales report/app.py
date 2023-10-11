from flask import Flask, render_template
import sqlite3
import plotly.graph_objs as go

app = Flask(__name__)

@app.route('/')
def index():
    # Connect to the SQLite database
    conn = sqlite3.connect("static/sales_data.db")
    cursor = conn.cursor()

    # Retrieve data from the database
    cursor.execute("SELECT Date, SUM(Quantity * Price) FROM Sales GROUP BY Date")
    data = cursor.fetchall()

    # Retrieve all_data from the database
    cursor.execute("select * FROM Sales ")
    all_data = cursor.fetchall()

    # Extract dates and sales revenue
    dates = [row[0] for row in data]
    revenue = [row[1] for row in data]

    # Calculate KPI values
    total_sales = len(all_data)
    total_sales_amount = sum(revenue)

    # Create a Plotly line chart
    chart = go.Figure(data=[go.Scatter(x=dates, y=revenue, mode='lines+markers', name='Sales Revenue')])
    chart.update_layout(title='Sales Revenue Over Time', xaxis_title='Date', yaxis_title='Revenue')

    # Convert the Plotly chart to HTML
    chart_html = chart.to_html(full_html=False)

    # Calculate sales data by product
    cursor.execute("SELECT Product, SUM(Quantity * Price) FROM Sales GROUP BY Product")
    product_data = cursor.fetchall()

    product_names = [row[0] for row in product_data]
    product_sales = [row[1] for row in product_data]

    # Create a Plotly donut chart
    donut_chart = go.Figure(data=[go.Pie(labels=product_names, values=product_sales, hole=0.4)])
    donut_chart.update_layout(title='Sales by Product')

    # Convert the Plotly donut chart to HTML
    donut_chart_html = donut_chart.to_html(full_html=False)

    return render_template('sales_chart.html', chart_html=chart_html, total_sales=total_sales,
                           total_sales_amount=total_sales_amount, donut_chart_html=donut_chart_html)

@app.route('/raw_data')
def raw_data():
    # Connect to the SQLite database
    conn = sqlite3.connect("static/sales_data.db")
    cursor = conn.cursor()

    # Retrieve all rows from the Sales table
    cursor.execute("SELECT * FROM Sales")
    sales_data = cursor.fetchall()
    conn.close()

    return render_template('sales_data_table.html', sales_data=sales_data)

if __name__ == '__main__':
    app.run(debug=True)
