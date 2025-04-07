
from datetime import datetime
import pyodbc
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import pandas as pd

load_dotenv()

print(pyodbc.drivers)


def connect_to_db(prefix) -> Engine:
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


def fetch_data(engine: Engine, table_fields: list[dict], manual_query : str = 0) -> dict:
    data = {}

    if(manual_query): # If you want to write your own queries s
        with engine.connect() as conn:
            results = conn.execute(text(manual_query)).fetchall()
            return [dict(row._mapping) for row in results]

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
def apply_transformations( data: list[dict]) -> list[dict]:
    transformed = []

    for row in data:
        new_row = row.copy()
        if 'LocalAnnotation' in row: # NOTE: add better handling to ensure output type is maintained
            new_row['LocalAnnotation'] = 'this is a test'  # Example logic
        
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


def export_transformed_data_to_file(transformed_batches: list[dict], output_dir='output', file_type='xlsx') -> None:
    """
    exports the transformed batches into an excel spreadsheet
    
    NOTE: this should be expanded to accomodate for changes spanning multiple fields across multiple tables such that 
    there is a new sheet for every new table effected
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"transformed_data_{timestamp}.xlsx")

    if not transformed_batches:
        print("No data to export.")
        return

    df = pd.DataFrame(transformed_batches)
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="TransformedData", index=False)

    print(f"[✓] Exported data to Excel file: {output_path}")
    



def main():
    source_conn = connect_to_db('HERP')
    target_conn = connect_to_db('SPECIFY')
    source_table_fields = [
        {'table': 'herp_rbase.MAINCAT', 'fields': ['id', 'catno']}
    ]

    # grabs data from source
    raw_data = fetch_data(source_conn, source_table_fields, manual_query='SELECT * from herp_rbase.MAINCAT limit 10;')

    # define your own transformations within the apply_transformations function
    transformed_batches = apply_transformations(raw_data)

    '''
    for i in transformed_batches:
        print(i)
    '''
    # export into an xlsx 
    export_transformed_data_to_file(transformed_batches=transformed_batches)

    




if __name__ == "__main__":
    main()
