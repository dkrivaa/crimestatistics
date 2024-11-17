import streamlit as st
import pandas as pd
import requests
import json
from collections import defaultdict
import time


# Base URL for the CKAN API
url = "https://data.gov.il/api/3/action/datastore_search"


# Return df from resource with all records - used to make menus
def get_df_from_resource(resource_id):
    offset = 0
    limit = 100000  # Fetch in chunks
    all_records = []

    while True:
        # Define API request parameters
        params = {
            "resource_id": resource_id,
            "limit": limit,
            "offset": offset,
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            st.write(f"Error fetching resource {resource_id}: {response.status_code}")
            break

        data = response.json()
        if not data.get("success"):
            st.write(f"Error in response for {resource_id}: {data.get('error')}")
            break

        # Extract records
        records = data["result"]["records"]
        if not records:
            break

        all_records.extend(records)
        offset += limit

    return pd.DataFrame(all_records)


# Getting quarterly data according to filter
def get_data(filters=None):
    if filters is None:
        filters = {}

    resource_dict = {
        '3b3cf0d8-67d9-4719-9dfa-f73ab7ab9f68': 2019,
        '520597e3-6003-4247-9634-0ae85434b971': 2020,
        '3f71fd16-25b8-4cfe-8661-e6199db3eb12': 2021,
        'a59f3e9e-a7fe-4375-97d0-76cea68382c1': 2022,
        '32aacfc9-3524-4fba-a282-3af052380244': 2023,
        '5fc13c50-b6f3-4712-b831-a75e0f91a17e': 2024,
    }

    quarter_list = ['Q1', 'Q2', 'Q3', 'Q4']

    # Initialize counts
    quarter_counts = defaultdict(lambda: defaultdict(int))  # year -> quarter -> count

    def process_resource(resource_id, year, filters, max_retries=3):
        offset = 0
        limit = 50000  # Fetch in chunks
        all_records = []
        retry_count = 0

        while retry_count < max_retries:
            try:
                while True:
                    params = {
                        "resource_id": resource_id,
                        "filters": json.dumps(filters),
                        "limit": limit,
                        "offset": offset,
                    }
                    response = requests.get(url, params=params)

                    if response.status_code != 200:
                        st.write(f"Error fetching resource {resource_id}: {response.status_code}")
                        raise ValueError(f"API Error: {response.status_code}")

                    data = response.json()
                    if not data.get("success"):
                        st.write(f"API Response Error: {data.get('error')}")
                        raise ValueError(f"API Response Error: {data.get('error')}")

                    records = data["result"].get("records", [])

                    if not records:  # No more records to fetch
                        break

                    all_records.extend(records)
                    offset += limit

                # Break out of retry loop on success
                break

            except ValueError as e:
                retry_count += 1
                st.write(f"Retry {retry_count}/{max_retries}: {e}")
                if retry_count >= max_retries:
                    st.write(f"Failed to process resource {resource_id} after {max_retries} retries.")
                    return []
                time.sleep(2 ** retry_count)  # Exponential backoff

            except Exception as e:
                st.write(f"Unexpected error: {e}")
                return []

        # Return all fetched records
        return all_records

    for resource_id, year in resource_dict.items():
        # st.write(f"Getting data for year {year}...")
        records = process_resource(resource_id, year, filters)

        # Count records by quarter
        for record in records:
            quarter = record.get('Quarter')  # Replace with actual quarter column name
            if quarter in quarter_list:
                match = all(record.get(k) == v for k, v in filters.items())
                if match:
                    quarter_counts[year][quarter] += 1

    # Sort the inner dictionaries by quarter
    for year in quarter_counts:
        quarter_counts[year] = dict(sorted(quarter_counts[year].items(), key=lambda item: item[0]))

    # Flatten quarter_counts into a list of {"Year-Quarter": value} rows
    data = []
    for year, quarters in quarter_counts.items():
        for quarter, count in sorted(quarters.items(), key=lambda x: x[0]):
            year_quarter = f"{year}-{quarter}"
            data.append({"Quarter": year_quarter, "Crimes": count})

    # Convert to DataFrame for output
    return pd.DataFrame(data)

