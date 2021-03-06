from dataflows import Flow, load, dump_to_path, dump_to_zip, printer
from dataflows import add_metadata, checkpoint
from dataflows import sort_rows, filter_rows, find_replace, delete_fields, set_type, validate, unpivot

import shutil
import os

import numpy as np
from pandas import read_csv

# *******************************************************************
# Load data utilities
# *******************************************************************
BASE_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
CONFIRMED = 'time_series_19-covid-Confirmed.csv'
DEATH = 'time_series_19-covid-Deaths.csv'
RECOVERED = 'time_series_19-covid-Recovered.csv'

def update_dataset():
    flow = Flow(
        # Load inputs
        load(f'{BASE_URL}{CONFIRMED}'),
        load(f'{BASE_URL}{RECOVERED}'),
        load(f'{BASE_URL}{DEATH}'),
        checkpoint('load_data'),
        # Process them (if necessary)
        # Save the results
        add_metadata(name='csse_covid_19_time_series', title='''csse_covid_19_time_series'''),
        printer(),
        dump_to_path(),
    )
    flow.process()

def clean_dataset():
    for name in ('Confirmed', 'Deaths', 'Recovered'):
        fname = 'time_series_19-covid-{}.csv'.format(name)
        if os.path.isfile(fname):
            os.remove(fname)

    fname = 'datapackage.json'
    if os.path.isfile(fname):
        os.remove(fname)
# *******************************************************************

# *******************************************************************
#  Read utilities
#  Returns a dataframe depending on the case: confirmed, deaths, recovered
# *******************************************************************
def read_data(case):
    fname = 'time_series_19-covid-{}.csv'.format(case)
    df = read_csv(fname)
    return df

def read_confirmed_cases():
    return read_data('Confirmed')

def read_recovered_cases():
    return read_data('Recovered')

def read_deaths_cases():
    return read_data('Deaths')
# *******************************************************************


def normalize_date(date):
    month, day, year = date.split('/')
    return '{day}/{month}'.format(day=day, month=month)


def select_data_by_country(df, country):
    key_selection = 'Country/Region'
    # TODO improve the case such as France
    if country == 'France':
        key_selection = 'Province/State'

    dc = df[df[key_selection] == country]
    to_remove = ('Province/State', 'Country/Region', 'Lat', 'Long')
    for a in to_remove:
        dc.pop(a)

    t, y = zip(*list(dc.items()))

    # new format
    y = np.array([int(_) for _ in y])
    t = list(map(normalize_date, t))

    return t,y


def plot_matplotlib(df):
    """
    used for testing
    """
    from matplotlib import pyplot as plt

    fig, ax = plt.subplots()

    countries = ['Morocco', 'Tunisia', 'Italy', 'Spain', 'France', 'Germany']

    for country in countries:
        t,y = select_data_by_country(df, country)

    #    ax.plot(t, y, '-', label=country)
        ax.semilogy(t, y, '-', label=country)
        ax.set_xticks(t[::7]+[t[-1]])
        ax.set_xlabel('Date',size=12,fontweight='semibold')
        ax.set_ylabel('Confirmed cases',size=12,fontweight='semibold')

    plt.legend()
    plt.show()


if __name__ == '__main__':
#    clean_dataset()
#    update_dataset()

    df = read_confirmed_cases()
    plot_matplotlib(df)
