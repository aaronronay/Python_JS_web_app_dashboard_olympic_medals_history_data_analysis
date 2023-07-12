from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, render_template
import pandas as pd
import sqlalchemy

# Change values to new credentials
database_username = 'root'
database_password = 'root'
database_ip = '127.0.0.1:3306'
database_name = 'olympics'
database_connection = f'mysql+mysqlconnector://{database_username}:{database_password}@{database_ip}/{database_name}'

# Flask Initialize
app = Flask(__name__)

# Database Setup
app.config["SQLALCHEMY_DATABASE_URI"] = database_connection
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

# Save references to each table
Master_data = db.Model.metadata.tables.get('master_data')

# Connect to MySQL server for query results
mysql_query = "SELECT * FROM olympics.master_data"

@app.route("/")
def index():
    '''Return to the homepage.'''
    return render_template('index.html')

@app.route("/data_no-variable/")
def data():
    """Return the JSON data"""
    try:
        return jsonify(get_cached_data())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/data2/")
def data2():
    """Return the JSON data"""
    try:
        return jsonify(get_cached_data2())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/summer/<year>")
def summer_year(year):
    """Return the JSON data"""
    try:
        return jsonify(get_cached_summer_year(year))
    except Exception as e:
        return jsonify({'error': str(e)})

def get_cached_data():
    try:
        if 'cached_data' not in app.config:
            dataframe = pd.read_sql(mysql_query, con=database_connection)
            app.config['cached_data'] = dataframe.to_dict(orient='records')
        return app.config['cached_data']
    except Exception as e:
        raise Exception('Error retrieving cached data') from e

def get_cached_data2():
    try:
        if 'cached_data2' not in app.config:
            stmt = db.session.query(Master_data).statement
            dataframe = pd.read_sql_query(stmt, db.session.bind)
            app.config['cached_data2'] = dataframe.to_dict(orient='records')
        return app.config['cached_data2']
    except Exception as e:
        raise Exception('Error retrieving cached data 2') from e

def get_cached_summer_year(year):
    try:
        cache_key = f"summer_{year}"
        if cache_key not in app.config:
            stmt = db.session.query(Master_data).filter(Master_data.c.season == "summer", Master_data.c.Year == year).statement
            dataframe = pd.read_sql_query(stmt, db.session.bind)
            app.config[cache_key] = dataframe.to_dict(orient='records')
        return app.config[cache_key]
    except Exception as e:
        raise Exception('Error retrieving cached summer year data') from e

if __name__ == "__main__":
    app.run()
