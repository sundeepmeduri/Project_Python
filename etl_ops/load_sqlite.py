import pandas as pd
import sqlite3

def load_csv_to_sqlite(csv_file, sqlite_db, table_name, chunksize=1000):
    """
    Load a CSV file into an SQLite table, inserting only columns that match.
    """
    # Connect to SQLite
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()

    # === Get existing table columns ===
    cursor.execute(f"PRAGMA table_info('{table_name}');")
    table_cols = [row[1] for row in cursor.fetchall()]
    print(f"Table columns in {table_name}: {table_cols}")

    # === Read CSV ===
    df = pd.read_csv(csv_file)
    print(f"CSV columns: {df.columns.tolist()}")

    # === Keep only matching columns ===
    common_cols = [c for c in df.columns if c in table_cols]
    if not common_cols:
        raise ValueError("No matching columns between CSV and SQLite table!")

    df = df[common_cols]
    print(f"Loading columns: {common_cols}")

    # === Insert in chunks for efficiency ===
    for i in range(0, len(df), chunksize):
        df.iloc[i:i+chunksize].to_sql(
            table_name, conn, if_exists="append", index=False
        )
        print(f"Inserted rows {i}–{i+chunksize}")

    conn.commit()
    conn.close()
    print(f"CSV data loaded into table '{table_name}' successfully.")


# === Example usage ===
load_csv_to_sqlite(
    csv_file="data.csv",
    sqlite_db="my_database.db",
    table_name="myschema_mytable"
)
