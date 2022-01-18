from src.data_handler import load_files
from src.data_handler import save_file
from src.data_handler import get_customer_country_distribution
from src.data_handler import get_inactive_license_users

from dash import html,dcc
import plotly.express as px



def load_data():
    """Loads the raw data files into memory.

    Parameters
    ----------

    Returns
    -------
    bool
        Returns True if data is successfully loaded.

    """
    load_files()
    print('Loaded raw data')
    return True


def get_simple_app_layout(id,title,subtitle,fig):
    """Returns an html Div to encapsulate a certain graph we want to show.

    Parameters
    ----------
    id : str
        Css id that will identify the figure.
    title : str
        Title that will be shown above the figure.
    subtitle : str
        Subtitle that will be shown above the figure.
    fig : plotly.graph_objects
        Figure that will hold the graph.

    Returns
    -------
    html.Div
        html.Div containing the data sent in the parameters.

    """

    return html.Div(className='row',children=[
        # All elements from the top of the page
        html.Div([
            html.H1(children=title),

            html.Div(children=subtitle),
            dcc.Graph(
                id=id,
                figure=fig
            ),
        ]),

    ])



def get_pie_chart_fig_countries(df):
    """Returns an figure that displays the data in df.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe that contains the fields ['country_code','accounts_country'].

    Returns
    -------
    plotly.express.pie
        Figure that will hold the graph.

    """
    df.loc[df['accounts_country'] <= 170, 'country_code'] = 'Other countries' # Represent only large countries
    fig = px.pie(df, values='accounts_country', names='country_code', title='Accounts per country')
    #fig.show()
    return fig



def get_bar_chart_fig_domain_hits(df):
    """Returns an figure that displays the data in df.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe that contains the fields ['domain','hits'].

    Returns
    -------
    plotly.express.bar
        Figure that will hold the graph.

    """
    fig = px.bar(df, x='domain', y='hits')
    #fig.show()
    return fig

def customer_country_distribution_html():
    """Returns the HTML displaying the data for customers per country.

    Parameters
    ----------

    Returns
    -------
    html.Div
        Html div containing everything for this functionality.

    """
    #we get the data
    data = get_customer_country_distribution()
    #we generate the figure
    fig = get_pie_chart_fig_countries(data)
    id = 'customer_country_distribution'
    title = 'Customers per Country'
    subtitle = 'Amount of client accounts we have per country'
    #we generate the div layout
    cur_html = get_simple_app_layout(id,title,subtitle,fig)
    return cur_html


def inactive_license_users_html(day):
    """Returns the HTML displaying the hits per domain in inactive licenses.

    Parameters
    ----------
    day : string
        User-inputted string represeting a day in YYYY-MM-DD format.

    Returns
    -------
    html.Div
        Html div containing everything for this functionality.

    """
    #we get the data
    data = get_inactive_license_users(day)

    #we generate the figures
    fig1 = get_bar_chart_fig_domain_hits(data['inactive'])
    id = 'inactive_license'
    title = 'Inactive domains'
    subtitle = f'Amount of hits we get per Domain in the day {day}'
    html1 = get_simple_app_layout(id,title,subtitle,fig1)

    fig2 = get_bar_chart_fig_domain_hits(data['noncrm'])
    id = 'noncrm'
    title = 'Domains not in CRM'
    subtitle = f'Amount of hits we get per Domain in the day {day}'
    html2 = get_simple_app_layout(id,title,subtitle,fig2)
    #we generate the div layout
    return html.Div([ html1,html2])


def create_all_csv():
    """Generates the csv for the two functionalities needed.

    Parameters
    ----------

    Returns
    -------
    bool
        Returns True if the csv are successfully created.

    """
    #we get the data for both functionalities
    data1 = get_inactive_license_users('2021-12-15')
    data2 = get_customer_country_distribution()

    save_file('customer_country_distribution', data2)
    save_file('inactive_license_domains', data1['inactive'])
    save_file('noncrm_domains', data1['noncrm'])

    return True
