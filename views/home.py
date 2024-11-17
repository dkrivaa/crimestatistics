import streamlit as st

from menus import make_crime_group_list, make_crime_type_list
from functions import get_data

st.title('Official Crime Data')
st.write('Quarterly data published by Israel Police (2019-2024)')
st.write("---")
st.subheader('Nationwide Data')

filters = {}

# Getting data
with st.spinner('Getting Data. This will just take a moment....'):
    if len(filters) == 0:
        df = get_data()
    else:
        df = get_data(filters)

# Crime group selection
crime_group = st.selectbox(label='Crime Group',
                           options=make_crime_group_list(),
                           index=None,
                           )

if crime_group:
    filters['StatisticCrimeGroup'] = crime_group
    # Crime type selection
    crime_type = st.selectbox(label='Crime Type',
                              options=make_crime_type_list(crime_group),
                              index=None)
    if crime_type:
        filters['StatisticCrimeType'] = crime_type

st.divider()

# Chart and dataframe
with st.container():
    if not crime_group:
        st.write('Total Crime Reported')
    elif crime_group and not crime_type:
        st.write(f'{crime_group}')
    else:
        st.write(f'{crime_group} - {crime_type}')

    st.line_chart(df, x='Quarter', y='Crimes', y_label='Total Crime', )

    st.dataframe(df, hide_index=True)





