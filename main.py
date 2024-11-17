import streamlit as st

home_page = st.Page(
    page='views/home.py',
    title='Home',
    default=True
)


pg = st.navigation(pages=[home_page, ])

pg.run()

