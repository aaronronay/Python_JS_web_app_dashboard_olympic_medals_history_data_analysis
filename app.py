import pandas as pd
import sqlalchemy
import pymysql
from flask import Flask, jsonify, render_template

# Change values to new credentials
database_username = 'root'
database_password = 'root'
database_ip = '127.0.0.1:3306'
database_name = 'olympics'
database_connection = f'mysql+mysqlconnector://{database_username}:{database_password}@{database_ip}/{database_name}'

# Flask Initialize
app = Flask(__name__)

# Set display options
pd.set_option('display.max_colwidth', -1)

# Read CSV files into DataFrames
csv_files = {
    'winter': 'data/winter.csv',
    'summer': 'data/summer.csv',
    'dictionary': 'data/dictionary.csv',
    'coord': 'data/country-capitals.csv',
    'maps': 'data/country_flags.csv'
}

dfs = {}
for name, path in csv_files.items():
    try:
        dfs[name] = pd.read_csv(path, encoding='utf-8')
    except FileNotFoundError as e:
        print(f"Error: {e}")

# Clean DataFrames
dfs['winter']['season'] = 'winter'
dfs['summer']['season'] = 'summer'

# Update Nan values in summer data
nan_updates = {
    (29603, 'Athlete'): 'Alptekin, Cakir',
    (29603, 'Country'): 'TUR',
    (31072, 'Athlete'): 'Maneza, Maiya',
    (31072, 'Country'): 'KAZ',
    (31091, 'Athlete'): 'Ilyin, Ilya',
    (31091, 'Country'): 'KAZ',
    (31110, 'Country'): 'RUS'
}
for (index, column), value in nan_updates.items():
    try:
        dfs['summer'].at[index, column] = value
    except KeyError as e:
        print(f"Error: {e}")

# Update country codes
country_code_updates = {
    'ANZ': 'NZL', 'BOH': 'CZE', 'BWI': 'JAM', 'EUA': 'GER', 'EUN': 'RUS', 'FRG': 'GER',
    'GDR': 'GER', 'IOP': 'SCG', 'MNE': 'SCG', 'ROU': 'ROM', 'RU1': 'RUS', 'SGP': 'SIN',
    'SRB': 'SCG', 'TCH': 'CZE', 'TTO': 'TRI', 'URS': 'RUS', 'YUG': 'SCG', 'ZZX': 'VARIOUS'
}
for df_name, df in dfs.items():
    try:
        df.replace(country_code_updates, inplace=True)
    except KeyError as e:
        print(f"Error: {e}")

# Rename columns
column_rename_dict = {'Country': 'Country_code'}
for df_name, df in dfs.items():
    try:
        df.rename(columns=column_rename_dict, inplace=True)
    except KeyError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")

# Combine DataFrames
try:
    merge_cols = ['Country_code', 'Country']
    master_data = pd.concat([dfs['summer'], dfs['winter']]).merge(dfs['dictionary'], on=merge_cols).merge(dfs['coord'], on=merge_cols).merge(dfs['maps'], on=merge_cols).dropna(subset=['Country_code']).reset_index(drop=True).reset_index().rename(columns={'index': 'id'})
except KeyError as e:
    print(f"Error: {e}")

# Upload master DataFrame to MySQL DB
try:
    pymysql.install_as_MySQLdb()
    database_connection = sqlalchemy.create_engine(database_connection)
    master_data.to_sql(name='master_data', con=database_connection, index=False, if_exists='replace', chunksize=1000)
except Exception as e:
    print(f"Error: {e}")

with database_connection.connect() as con:
    try:
        con.execute('ALTER TABLE `olympics`.`master_data` ADD PRIMARY KEY (`id`);')
    except Exception as e:
        print(f"Error: {e}")

# Connect to MySQL server for query results
try:
    query = "SELECT * FROM olympics.master_data"
    mysql_query_df = pd.read_sql(query, con=database_connection)
    json_data = mysql_query_df.to_json(orient='records')
except Exception as e:
    print(f"Error: {e}")
    json_data = {}

# Routes
@app.route("/")
def index():
    '''Return to the homepage.'''
    return render_template('index.html')

@app.route("/map")
def map():
    '''Return to the map visual.'''
    return render_template('map.html')

@app.route("/data")
def data():
    """Return the JSON data"""
    return jsonify(json_data)

if __name__ == "__main__":
    app.run()
