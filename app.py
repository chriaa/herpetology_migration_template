
import pyodbc
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

load_dotenv()

print(pyodbc.drivers)


def connect_to_db(prefix):
    host = os.getenv(f"{prefix}_DB_HOST")
    port = os.getenv(f"{prefix}_DB_PORT", 3306)
    database = os.getenv(f"{prefix}_DB_DATABASE")
    user = os.getenv(f"{prefix}_DB_USER")
    password = os.getenv(f"{prefix}_DB_PASSWORD")

    if not all([host, port, database, user, password]):
        raise ValueError(f"Missing database configuration for prefix '{prefix}'.")

    # Create the SQLAlchemy engine using pymysql
    connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_url)

    return engine


def fetch_data(engine: Engine, table_fields: list[dict]) -> dict:
    data = {}
    with engine.connect() as conn:
        for entry in table_fields:
            table = entry['table']
            fields = entry['fields']
            query = text(f"SELECT {', '.join(fields)} FROM {table}")
            results = conn.execute(query).fetchall()
            data[table] = {
                'fields': fields,
                'rows': [dict(row._mapping) for row in results]
            }
    return data

#Implement with pyspark
def apply_transformations(table: str, data: list[dict]) -> list[dict]:
    transformed = []

    for row in data:
        new_row = row.copy()
        if 'catno' in row and isinstance(row['catno'], int):
            new_row['catno'] = row['catno'] + 1  # Example logic
        # Add other transformations as needed per field/table
        transformed.append(new_row)

    return transformed


def export_transformed_data(engine: Engine, export_config: list[dict], transformed_batches: dict):
    """
    export_config: list of {'table': str, 'key': str, 'fields': list[str]}
    transformed_batches: matching dict with structure {table: [rows]}
    """
    with engine.begin() as conn:
        for config in export_config:
            table = config['table']
            key = config['key']
            fields = config['fields']

            for row in transformed_batches.get(table, []):
                update_fields = ', '.join([f"{field} = :{field}" for field in fields])
                query = text(f"""
                    UPDATE {table}
                    SET {update_fields}
                    WHERE {key} = :{key}
                """)
                conn.execute(query, row)


def export_transformed_data_to_file(transformed_batches: dict, output_dir='output', file_type='xlsx'):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if file_type == 'xlsx':
        output_path = os.path.join(output_dir, f"transformed_data_{timestamp}.xlsx")
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            for table_name, rows in transformed_batches.items():
                if rows:
                    df = pd.DataFrame(rows)
                    df.to_excel(writer, sheet_name=table_name[:31], index=False)  # Excel sheet names max 31 chars
        print(f"[✓] Exported all tables to Excel file: {output_path}")

    elif file_type == 'csv':
        for table_name, rows in transformed_batches.items():
            if rows:
                df = pd.DataFrame(rows)
                file_name = f"{table_name.replace('.', '_')}_{timestamp}.csv"
                csv_path = os.path.join(output_dir, file_name)
                df.to_csv(csv_path, index=False)
                print(f"[✓] Exported {table_name} to CSV: {csv_path}")
    else:
        raise ValueError("file_type must be 'xlsx' or 'csv'")
    



def main():
    source_conn = connect_to_db('HERP')
    target_conn = connect_to_db('SPECIFY')
    source_table_fields = [
        {'table': 'herp_rbase.MAINCAT', 'fields': ['id', 'catno']},
        {'table': 'herp_rbase.LOCALITY', 'fields': ['id', 'locname']}
    ]

    target_config = [
    ]

    print("Fetching source data...")
    raw_data = fetch_data(source_conn, source_table_fields)



if __name__ == "__main__":
    main()
