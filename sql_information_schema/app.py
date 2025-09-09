from flask import Flask, render_template, request
import pyodbc, json

app = Flask(__name__)


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

    try:
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                              f'SERVER={conf["server"]};'
                              f'DATABASE={conf["database"]};Trusted_Connection=yes')
        cursor = conn.cursor()
        print(f'database connection successful on server: {conf["server"]}')
        return cursor

    except Exception as e:
        print(f"Database connection failed --> {e}")


@app.route("/", methods=["GET", "POST"])
def home():
    search_query = request.form.get("search", "").strip()

    # Get all tables from INFORMATION_SCHEMA
    conf = get_db_config('1')
    cursor = db_conn(conf)
    print(search_query)

    if search_query:
        cursor.execute("""
            SELECT t.TABLE_SCHEMA, t.TABLE_NAME, COUNT(c.COLUMN_NAME) as column_count
            FROM INFORMATION_SCHEMA.TABLES t
            LEFT JOIN INFORMATION_SCHEMA.COLUMNS c
                ON t.TABLE_SCHEMA = c.TABLE_SCHEMA
                AND t.TABLE_NAME = c.TABLE_NAME
            WHERE (t.TABLE_NAME LIKE ? OR c.COLUMN_NAME LIKE ?) and TABLE_TYPE = 'BASE TABLE'
            GROUP BY t.TABLE_SCHEMA, t.TABLE_NAME
            ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
        """, ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute("""
            SELECT t.TABLE_SCHEMA, t.TABLE_NAME, COUNT(c.COLUMN_NAME) as column_count
            FROM INFORMATION_SCHEMA.TABLES t
            LEFT JOIN INFORMATION_SCHEMA.COLUMNS c
                ON t.TABLE_SCHEMA = c.TABLE_SCHEMA
                AND t.TABLE_NAME = c.TABLE_NAME
            WHERE TABLE_TYPE = 'BASE TABLE'    
            GROUP BY t.TABLE_SCHEMA, t.TABLE_NAME
            ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
        """)
    # cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES ")
    tables = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
    cursor.close()
    return render_template("home.html", tables=tables, search_query=search_query)


@app.route("/schema/<table_name>")
def schema(table_name):
    # Get schema details for selected table
    conf = get_db_config('1')
    cursor = db_conn(conf)
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ?
    """, (table_name,))
    columns = cursor.fetchall()
    cursor.close()
    return render_template("schema.html", table_name=table_name, columns=columns)


@app.route("/analyze/<schema_name>/<table_name>", methods=["GET", "POST"])
def analyze(schema_name, table_name):
    conf = get_db_config('1')
    cursor = db_conn(conf)

    # --- Row count ---
    cursor.execute(f"SELECT COUNT(*) FROM [{schema_name}].[{table_name}]")
    row_count = cursor.fetchone()[0]

    # --- Get all columns for dropdown ---
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """, (schema_name, table_name))
    all_columns = [row[0] for row in cursor.fetchall()]

    # --- Handle selected columns from form ---
    selected_columns = request.form.getlist("columns")  # multiple select
    if selected_columns:
        col_str = ", ".join(f"[{col}]" for col in selected_columns)
    else:
        col_str = "*"   # default all columns
        selected_columns = all_columns  # for rendering headers

    # --- Sample rows (first 5) with selected columns ---
    cursor.execute(f"SELECT TOP 5 {col_str} FROM [{schema_name}].[{table_name}]")
    sample_rows = cursor.fetchall()
    sample_columns = [desc[0] for desc in cursor.description]
    rows_as_dict = [dict(zip(sample_columns, row)) for row in sample_rows]

    # --- Table schema ---
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """, (schema_name, table_name))
    schema_columns = cursor.fetchall()

    cursor.close()
    return render_template(
        "analyze.html",
        schema_name=schema_name,
        table_name=table_name,
        row_count=row_count,
        sample_columns=sample_columns,
        sample_rows=rows_as_dict,
        schema_columns=schema_columns,
        all_columns=all_columns,
        selected_columns=selected_columns
    )


if __name__ == "__main__":
    app.run(debug=True)
