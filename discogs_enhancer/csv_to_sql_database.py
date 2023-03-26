import psycopg2
import os
import csv
import bz2
import sys
conn = psycopg2.connect(
    host="localhost",
    dbname="Discogs_Data",
    user="postgres",
    password=os.getenv('PASSWORD'),
    port="5432"
)

cur = conn.cursor()

csv.field_size_limit(sys.maxsize)

csv_dir = '/Users/justinpak/code/justinpakzad/discogs_advanced_searching/csv-dir'
for file in os.listdir(csv_dir):

    if file.endswith('.csv.bz2'):
        table_name = file.replace('.csv.bz2','')
        print(f"Loading {table_name}")
        with bz2.open(os.path.join(csv_dir,file),'rt') as f:
            reader = csv.reader(f)
            header = next(reader)
            print(header)
            cur.execute(f"DROP TABLE IF EXISTS {table_name};")
            cur.execute(f"CREATE TABLE {table_name} ({', '.join([f'{col} TEXT' for col in header])});")
            # Try and check to see if theres any errors (;
            for i, row in enumerate(reader):
                try:
                    cur.execute(f"INSERT INTO {table_name} ({', '.join(header)}) VALUES ({', '.join(['%s' for _ in row])})", row)
                except Exception as e:
                    print(f"Error occurred on row {i+1}: {e}")
            conn.commit()
        print(f'{table_name} loaded correctly!!!!')
