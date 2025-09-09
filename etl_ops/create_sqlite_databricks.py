import pandas as pd
import sqlite3

# === CONFIG ===
csv_file = "columns_metadata.csv"   # Your exported CSV from information_schema.columns
sqlite_db = "my_database.db"        # SQLite DB file to be created

# === STEP 1: Read metadata CSV ===
df = pd.read_csv(csv_file)

# Expected columns from information_schema.columns
# Adjust names if different in your CSV
# Usually includes: table_schema, table_name, column_name, data_type, ordinal_position
print("CSV Columns:", df.columns.tolist())

# === STEP 2: Create SQLite connection ===
conn = sqlite3.connect(sqlite_db)
cursor = conn.cursor()

# === STEP 3: Generate CREATE TABLE statements ===
# SQLite doesn’t support all Databricks types, so we map them
type_mapping = {
    "string": "TEXT",
    "varchar": "TEXT",
    "char": "TEXT",
    "boolean": "INTEGER",
    "int": "INTEGER",
    "bigint": "INTEGER",
    "smallint": "INTEGER",
    "tinyint": "INTEGER",
    "double": "REAL",
    "float": "REAL",
    "decimal": "REAL",
    "date": "TEXT",
    "timestamp": "TEXT"
}

# Group columns by table
for (schema, table), group in df.groupby(["table_schema", "table_name"]):
    cols = []
    for _, row in group.sort_values("ordinal_position").iterrows():
        col_name = row["column_name"]
        data_type = row["data_type"].lower()
        sqlite_type = type_mapping.get(data_type, "TEXT")  # default to TEXT if unknown
        cols.append(f'"{col_name}" {sqlite_type}')

    create_stmt = f'CREATE TABLE IF NOT EXISTS "{schema}_{table}" ({", ".join(cols)});'
    print("Creating:", create_stmt)
    cursor.execute(create_stmt)

# === STEP 4: Commit and close ===
conn.commit()
conn.close()
print(f"SQLite database '{sqlite_db}' created successfully.")
