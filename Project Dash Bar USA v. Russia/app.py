import pandas as pd
import sqlalchemy
import dash
import dash_core_components as dcc
import dash_html_components as html

# Define the database connection details
database_connection = 'mysql+mysqlconnector://root:060415Pame$@127.0.0.1:3306/olympics'

# Read data from the database
df = pd.read_sql_table('master_data', con=database_connection)

# Define the medal counts for USA and Russia
usa_medal_counts = df[df['Country_code'] == 'USA']['Medal'].value_counts()
rus_medal_counts = df[df['Country_code'] == 'RUS']['Medal'].value_counts()

# Define the Dash application and layout
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('Olympic Medals, 1896-2014'),
    html.Div('Dash: The summer and winter medal count between two nations.'),
    dcc.Graph(
        figure={
            'data': [
                {'x': usa_medal_counts.index, 'y': usa_medal_counts.values, 'type': 'bar', 'name': 'USA'},
                {'x': rus_medal_counts.index, 'y': rus_medal_counts.values, 'type': 'bar', 'name': 'RUSSIA'},
            ],
            'layout': {'title': 'America vs. Russia'}
        }
    )
])

# Run the application
if __name__ == "__main__":
    app.run_server(debug=True)
