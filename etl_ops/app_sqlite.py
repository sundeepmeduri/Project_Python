from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

DB_PATH = "my_database.db"
TABLE_NAME = "myschema_mytable"   # change this to your table


def get_table_data(table_name):
    """Fetch all rows + column names from an SQLite table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name};")
    col_names = [desc[0] for desc in cursor.description]  # dynamic column names
    rows = cursor.fetchall()

    conn.close()
    return col_names, rows


@app.route("/")
def index():
    col_names, rows = get_table_data(TABLE_NAME)
    return render_template("table.html", columns=col_names, rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
