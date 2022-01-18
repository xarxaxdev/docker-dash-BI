import pandas as pd
import numpy as np
import re,itertools


#default values so that they are declared
allowed_origins = pd.DataFrame()
account_countries = pd.DataFrame()
server_logs = pd.DataFrame()

#constant to have all non-printable input characters
control_chars = ''.join(map(chr, itertools.chain(range(0x00,0x20), range(0x7f,0xa0))))
control_char_re = re.compile('[%s]' % re.escape(control_chars))


def to_FQDN(domain):
    """Cleanup transformations to try and leave domain as fully qualified.
    Also remove non-printable inputs.

    Parameters
    ----------
    domain : str
        User-inputted string represeting a domain.

    Returns
    -------
    string
        Cleaned up FQDN if the input was an url else empty string.

    """

    #TO-DO: find a good library that replaces all our regex matching
    if(type(domain)!= type('I am a string')):
        return ''
    domain = control_char_re.sub('', domain)
    domain = domain.lower()
    #remove possible protocols(not a comprehensive list)
    domain = re.sub(r"^http://","",domain)
    domain = re.sub(r"^https://","",domain)
    domain = re.sub(r"^ftp://","",domain)
    domain = re.sub(r"^\*\.","",domain)#remove wildcard
    domain = domain.split('?')[0]#remove api query
    domain = domain.split('/')[0]#remove subpaths
    domain = domain.split(':')[0]#remove port
    pat = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")
    #we only care about domains
    if (pat.match(domain)):
        return ''


    #test-notes:
    #I came across the old specification where characters allowed are:
    # [a-z][0-9][-]
    #However there exist several websites whose characters are not so limited,
    # e.g: เก่งเลขประถม.com/backend in allowed_origins
    #so for a test I'll do simplified cleanup
    return domain


def load_files():
    """Loads the raw data files into memory.

    Parameters
    ----------

    Returns
    -------
    string
        Returns an empty string if successful and an error if not.
    """
    #test-notes:
    #in a more realistic environment we would load this from
    #some url, from some connection to a database. Maybe this function
    #would not exist and we would query the db directly.


    data_path = 'test_data/'
    #we load the data on global variables
    global allowed_origins
    global account_countries
    global server_logs

    try:
        allowed_origins = pd.read_json(
            data_path+ 'allowed_origins.jsonl',
            lines= True
            )
        #we do some cleanup on manually introduced fields
        allowed_origins['domain'] = allowed_origins['domain'].apply(to_FQDN)
    except ValueError:
        return 'Error happened while loading allowed_origins'

    try:
        account_countries = pd.read_csv(
            data_path+ 'account_countries.csv')
    except ValueError:
        return 'Error happened while loading account_countries'

    try:

        server_logs = pd.read_csv(
            data_path+ 'server_logs.csv')
        #we are losing some info by changing from urls, to domains, but nothing
        #relevant to our functionalities
        server_logs['referrer'] = server_logs['referrer'].apply(to_FQDN)
        server_logs= server_logs[server_logs['referrer']!= 'system.uri url']
        server_logs= server_logs[server_logs['referrer']!= 'localhost']

    except ValueError:
        return 'Error happened while loading server_logs'

    return ''

def get_customer_country_distribution():
    """Returns the active license(BasicUsage,Active) country metrics.

    Parameters
    ----------

    Returns
    -------
    pandas.DataFrame
        account_id amount per country in the order (country_code,accounts_country).

    """

    #test:I assume basic usage is a more limited license version of Active

    #select active license ids
    subselect = allowed_origins[allowed_origins['license_status'].isin(['BasicUsage','Active'])]
    subselect = subselect['account_id'].unique()

    #use active license ids as filtering condition to filter country rows
    select = account_countries[account_countries['account_id'].isin(subselect)]
    #calculate amount of rows per country
    result = select.groupby(by=['country_code'],dropna=False).size().reset_index(name='accounts_country')

    return result


def get_inactive_license_users(day):
    """Returns the inactive license domains (Trial,Inactive) given a certain day.

    Parameters
    ----------
    day : str
        User-inputted string represeting a day in YYYY-MM-DD format.

    Returns
    -------
    dict
        Dict with 2 fields; inactive and noncrm each containing a
        pandas.DataFrame, descending by amount of hits in the shape
        (domain,hits,account_id).

    """


    #function to leave only hostname domain and TLD
    to_domain = lambda x:'.'.join(x.split('.')[-2:])

    #test-notes:I assume basic usage is a more limited license version of Active

    ###ORIGINS PREPARATION###
    #we filter out uninteresting rows
    origins_subselect = allowed_origins[allowed_origins['license_status'].isin(['Trial','Inactive'])]
    #simplify for the join
    origins_subselect = origins_subselect[['account_id','domain']].drop_duplicates()
    #remove hostnames
    origins_subselect['domain'] = origins_subselect['domain'].apply(to_domain)

    ###LOGS PREPARATION###
    #we filter out uninteresting rows
    logs_subselect = server_logs[server_logs['timestamp'].apply(lambda x:x[:10]) == day]
    #rename for the join
    logs_subselect = logs_subselect.rename(columns ={'referrer':'domain'})
    #remove hostnames
    logs_subselect['domain'] = logs_subselect['domain'].apply(to_domain)
    #count hits per domain
    domain_hits = logs_subselect.groupby(by='domain').size().reset_index(name='hits')
    domain_hits = domain_hits[domain_hits['domain'] != '']

    ###MERGING### to know which is the associated account_id to a domain hits
    #and remove the Active licenses

    #we do a left join to keep the domains missing in the CRM
    joined = pd.merge(domain_hits,origins_subselect, on='domain', how='left').drop_duplicates()
    #finally we remove the files with null account_id(no match) that were in allowed_origins
    joined_noncrm = joined[~joined['domain'].isin(allowed_origins['domain'].apply(to_domain))]
    joined = joined.dropna()
    ###CLEANUP###
    joined_noncrm = joined_noncrm.drop('account_id',axis=1).drop_duplicates()
    joined_noncrm = joined_noncrm.sort_values('hits',ascending= False)
    joined = joined.drop('account_id',axis=1).drop_duplicates()
    joined = joined.sort_values('hits',ascending= False)

    return {'inactive':joined, 'noncrm':joined_noncrm}

def save_file(name, data):
    """Saves the raw data files into memory.

    Parameters
    ----------
    name : str
        File name for the data that will be saved.
    data : pandas.DataFrame
        Data to be saved into a csv.

    Returns
    -------
    bool
        Returns an empty string if successful and an error if not.
    """
    #test-notes:
    #in a more realistic environment we would load this from
    #some url, from some connection to a database. Maybe this function
    #would not exist and we would query the db directly.


    data_path = 'output_data/'

    try:
        data.to_csv(f'{data_path}{name}.csv',index=False)
    except ValueError:
        return 'Error happened while loading server_logs'

    return ''
