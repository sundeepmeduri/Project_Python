import pyodbc
import json
import csv
from datetime import datetime
import time


def main():

    start_time = time.time()
    current_datetime = datetime.now()
    print(f'--> start time: {current_datetime.strftime("%H:%M:%S")}')

    job_exec('1', '1')

    current_datetime = datetime.now()
    print(f'--> end time: {current_datetime.strftime("%H:%M:%S")}')
    end_time = time.time()
    print(f'--> Total time taken: {end_time - start_time} Secs')


def job_exec(db_id, query_id):

    conf = get_db_config(db_id)
    cursor = db_conn(conf)

    query, csv_file = get_query(query_id)
    data, cols = select_query(cursor, query)

    write_csv(csv_file, data, cols)


def get_query(query_id):

    try:
        with open('query.json', 'r') as file:
            data = json.load(file)
            return data[query_id]
    except FileNotFoundError:
        print(f"Error: {file} not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file}.")


def get_db_config(db_id):

    try:
        with open('db_config.json', 'r') as file:
            data = json.load(file)
            return data[db_id]
    except FileNotFoundError:
        print(f"Error: {file} not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file}.")


def db_conn(conf):

    # Establish the connection
    try:
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                              f'SERVER={conf["server"]};'
                              f'DATABASE={conf["database"]};Trusted_Connection=yes')
                              # f'UID={username};'
                              # f'PWD={password}')
        cursor = conn.cursor()
        print(f'database connection successful on server: {conf["server"]}')
        return cursor

    except Exception as e:
        print(f"Database connection failed --> {e}")


def select_query(cursor, query):

    cursor.execute(query)
    rows = cursor.fetchall()
    print(f'Number of records: {len(rows):,}')

    columns = [column[0] for column in cursor.description]
    cursor.close()
    return rows, columns


def write_csv(csv_file, data, cols):

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='|')

    # Write the column names (optional)
        writer.writerow(cols)

    # Write the rows to the CSV
        recs = 0
        cnt = 0
        for row in data:
            cnt += 1
            recs += 1
            if cnt == 10000:
                cnt = 0
                print(f'Number of records written: {recs:,}')
            writer.writerow(row)

    print(f'Total records written: {recs:,}')


main()
