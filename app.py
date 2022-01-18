import datetime
from src.call_handler import load_data
from src.call_handler import create_all_csv
from src.call_handler import customer_country_distribution_html
from src.call_handler import inactive_license_users_html
import dash
from dash import html,dcc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    #the 2 links we want to show
    dcc.Link('Navigate to "/unverified_trials/2021-12-15"', href='/unverified_trials/2021-12-15'),
    html.Br(),
    dcc.Link('Navigate to "/customer_country_distribution"', href='/customer_country_distribution'),

    # content will be rendered in this element
    html.Div(id='page-content')
])

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])





def display_page(pathname):
    """Loads whichever html is being requested according to the path.

    Parameters
    ----------
    pathname : string
        Path after the first '/' in the url.

    Returns
    -------
    html.Div
        Html div containing all the figures for the requested functionality.

    """
    if ('unverified_trials' in pathname):
        path = pathname.replace('/unverified_trials/','')
        if validate(path):
            date = path
        else:
            date = '2021-12-15'
        return inactive_license_users_html(date)
    if ('customer_country_distribution' in pathname):
        return customer_country_distribution_html()
    return html.Div([
        html.H3('Click above to test the data being displayed')
    ])



#test-notes: not stricly necessary, but I want the app not to crash
def validate(date_text):
    """Returns whether date_text has a day shape with error handling.

    Parameters
    ----------
    date_text : string
        Date in the format YYYY-MM-DD.

    Returns
    -------
    bool
        Returns True if date_text has a day shape else False.

    """
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        return False
    return True



if __name__ == "__main__":
    load_data()#we load the data only once at the beginning
    create_all_csv()#we generate the csv at the beginning
    app.run_server(host='0.0.0.0',port=5000)
