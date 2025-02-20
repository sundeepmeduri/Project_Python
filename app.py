from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return "Welcome to Power Query ETL!"

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if the POST request has a file part
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return "No selected file"

        if file:
            # Save the uploaded file to the upload folder
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            # Read the uploaded file
            df = pd.read_csv(filename)

            # Get column names and data types
            column_info = df.dtypes.reset_index()
            column_info.columns = ['Column Name', 'Data Type']

            # Get the number of records
            num_records = len(df)

            # Render the file_info.html template with file name, column names, data types, and number of records
            return render_template('file_info.html', filename=file.filename, column_info=column_info.to_html(classes='table table-bordered table-striped', index=False), num_records=num_records)

    return render_template('upload.html')

@app.route('/filter_data/<filename>', methods=['GET', 'POST'])
def filter_data(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "File not found."

    df = pd.read_csv(file_path)
    num_records = len(df)
    columns = df.columns.tolist()

    filtered_data = df.copy()

    if request.method == 'POST':
        # Apply filters based on user input
        for column in columns:
            filter_value = request.form.get(column, '').strip()
            if filter_value:
                try:
                    # Try to convert the filter value to the appropriate data type of the column
                    if df[column].dtype == 'int64' or df[column].dtype == 'float64':
                        filter_value = float(filter_value)
                    elif df[column].dtype == 'datetime64':
                        filter_value = pd.to_datetime(filter_value)

                    # Apply the filter
                    filtered_data = filtered_data[filtered_data[column] == filter_value]
                except ValueError:
                    # Handle invalid filter values here
                    pass

    filtered_data = filtered_data.values.tolist()

    return render_template('filter_data.html', filename=filename, num_records=num_records, columns=columns,
                           filtered_data=filtered_data)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
----------------------------------------

from flask import Flask, jsonify
import pyodbc

app = Flask(__name__)

# Configure SQL Server connection
server = 'your_server'
database = 'your_database'
username = 'your_username'
password = 'your_password'
driver = '{ODBC Driver 17 for SQL Server}'

connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def get_db_connection():
    return pyodbc.connect(connection_string)

@app.route('/table1', methods=['GET'])
def get_table1_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, value FROM table1")
        records = cursor.fetchall()
        conn.close()
        data = [{'id': rec[0], 'name': rec[1], 'value': rec[2]} for rec in records]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/table2', methods=['GET'])
def get_table2_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, description, amount FROM table2")
        records = cursor.fetchall()
        conn.close()
        data = [{'id': rec[0], 'description': rec[1], 'amount': rec[2]} for rec in records]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
