import json

# Dictionary defining the table schema
column_schema = {
    'OBJECTID': 'INTEGER',
    'BLDG_ID': 'INTEGER',
    'BLDG_NAME': 'VARCHAR(255)',
    'ADDRESS': 'VARCHAR(255)',
    'CITY': 'VARCHAR(100)',
    'ZIPCODE': 'VARCHAR(10)',
    'CSP_SCH_ID': 'INTEGER',
    'SCH_ID': 'INTEGER',
    'SCH_NAME': 'VARCHAR(255)',
    'SCH_LABEL': 'VARCHAR(100)',
    'SCH_TYPE': 'VARCHAR(50)',
    'SHARED': 'VARCHAR(50)',
    'COMPLEX': 'VARCHAR(50)',
    'Label': 'INTEGER',
    'TLT': 'INTEGER',
    'PL': 'VARCHAR(100)',
    'POINT_X': 'DOUBLE PRECISION',
    'POINT_Y': 'DOUBLE PRECISION',
    'geom': 'GEOMETRY(Point, 4326)'
}

# Path to your GeoJSON file
geojson_file_path = 'Boston Public Schools - PostGIS/data/Public_Schools.geojson'

# Path to save the generated SQL file
output_sql_file_path = 'Boston Public Schools - PostGIS/pg_scripts/3_insert_statements.sql'

# Function to generate the INSERT INTO statement
def generate_insert_statement(table_name, feature, schema):
    properties = feature['properties']
    geometry = feature['geometry']

    columns = []
    values = []

    for column_name in schema.keys():
        if column_name == 'geom':
            # Handle geometry separately
            if geometry and geometry.get('type') == 'Point':
                coordinates = geometry.get('coordinates')
                if coordinates:
                    longitude = coordinates[0]
                    latitude = coordinates[1]
                    geom_value = f"ST_SetSRID(ST_Point({longitude}, {latitude}), 4326)"
                    values.append(geom_value)
                else:
                    values.append('NULL')
            else:
                values.append('NULL')
        else:
            value = properties.get(column_name)
            if value is None:
                values.append('NULL')
            elif isinstance(value, str):
                value = value.replace("'", "''")  # Escape single quotes
                values.append(f"'{value}'")
            else:
                values.append(str(value))

        columns.append(column_name)

    columns_list = ", ".join(columns)
    values_list = ", ".join(values)
    insert_sql = f"INSERT INTO {table_name} ({columns_list}) VALUES ({values_list});"
    return insert_sql

# Main script
def main():
    table_name = 'buildings'

    try:
        # Load GeoJSON data
        with open(geojson_file_path, 'r') as file:
            geojson_data = json.load(file)

        # List to hold generated SQL statements
        sql_statements = []

        # Iterate over each feature in the GeoJSON and generate INSERT statements
        for feature in geojson_data.get('features', []):
            insert_sql = generate_insert_statement(table_name, feature, column_schema)
            sql_statements.append(insert_sql)

        # Save the generated SQL statements to a file
        with open(output_sql_file_path, 'w') as sql_file:
            sql_file.write("\n".join(sql_statements))

        print(f"SQL file '{output_sql_file_path}' has been created successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()