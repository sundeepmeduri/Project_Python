from flask import Flask, render_template, request
import pyodbc

app = Flask(__name__)

server_name = "DESKTOP-MFHH6CQ\SQLEXPRESS01"
database_name = "etl_operations"
table_name = 'etljobloadstatus'


# Function to calculate job counts by status
def calculate_job_counts():
    connection = pyodbc.connect(
        f"DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};")
    cursor = connection.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM {table_name} ")
    total_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE Status = 'Success'")
    success_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE Status = 'Failure'")
    failure_count = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE Status = 'Error'")
    error_count = cursor.fetchone()[0]

    connection.close()

    return total_count, success_count, failure_count, error_count


# Function to fetch job statuses from the database based on status filter
def fetch_job_statuses(status_filter=None):
    connection = pyodbc.connect(
        f"DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};")
    cursor = connection.cursor()

    query = f"SELECT * FROM {table_name}"

    if status_filter:
        query += f" WHERE Status = '{status_filter}'"

    cursor.execute(query)
    job_statuses = cursor.fetchall()

    connection.close()

    return job_statuses


@app.route('/', methods=['GET', 'POST'])
def index():
    # Calculate job counts for Success, Failure, and Error
    total_count, success_count, failure_count, error_count = calculate_job_counts()

    # Get status filter from form submission
    status_filter = request.form.get('statusFilter')

    # Fetch job statuses based on the selected filter
    job_statuses = fetch_job_statuses(status_filter)

    # Render the HTML template to display the data
    return render_template('index.html', job_statuses=job_statuses, total_count=total_count,
                           success_count=success_count, failure_count=failure_count, error_count=error_count)


if __name__ == '__main__':
    app.run(debug=True)
