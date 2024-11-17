import streamlit as st
import pandas as pd

from functions import get_df_from_resource

# Base URL for the CKAN API
url = "https://data.gov.il/api/3/action/datastore_search"

# Make crime group list
def make_crime_group_list():
    resource_id = 'b53b64f8-57ed-4213-9191-a7401c0cf436'
    df = get_df_from_resource(resource_id)
    return df['StatisticCrimeGroup'].unique().tolist()


def make_crime_type_list(crime_group):
    resource_id = 'b53b64f8-57ed-4213-9191-a7401c0cf436'
    df = pd.DataFrame(get_df_from_resource(resource_id))
    df = df.loc[df['StatisticCrimeGroup'] == crime_group]
    return df['StatisticCrimeType'].unique().tolist()
