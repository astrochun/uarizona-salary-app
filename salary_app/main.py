#!/usr/bin/env python3
import argparse

import streamlit as st
from streamlit.components.v1 import html

import pandas as pd

from constants import COLLEGE_NAME, FY_LIST, TITLE
import sidebar
import views


@st.cache
def load_data(local: str = ''):
    """Load data"""
    if local:
        print("Loading data from local source")
    else:
        print("Loading data from Google Drive")

    file_id = {
        'FY2019-20': '1d2l29_T-mOh05bglPlwAFlzeV1PIkRXd',
        'FY2018-19': '1paxrUyW1wZuK3bjSL_L7ckKEC6xslZJe',
        'FY2017-18': '1AnRaPpbRTLVyqdeqe6vkPMYgbNnw9zia',
        'FY2016-17': '1rXBuuXit5oWKtfnA05gsNtsWAyESeIs2',
        'FY2014-15': '1ZANVDr6Kw40MJYiOENWbLMTFEMWyf7f4',
        'FY2013-14': '1rQ8A2CIVhDYu0lESKVh72h6VUd8gIEFl',
        'FY2011-12': '1fQOzEHiOvc_H1NcLMlK3KVV1DJkRbRuX',
    }

    data_dict = {}
    for year in FY_LIST:
        year_split = year.split(' ')[0]
        if not local:
            url = f'https://drive.google.com/uc?id={file_id[year_split]}'
        else:
            url = f'{local}/{year_split}_clean.csv'
        data_dict[year_split] = pd.read_csv(url)

    # Get unique.csv
    if not local:
        unique_url = 'https://drive.google.com/uc?id=1-2aFLO1nbPWT02y8N8Suue0Gg2FisWub'
    else:
        unique_url = f'{local}/unique.csv'
    unique_df = pd.read_csv(unique_url)

    return data_dict, unique_df


@st.cache
def header_buttons() -> str:
    """Return white-background version of GitHub Sponsor button"""
    file_name = "assets/header_buttons.html"
    with open(file_name, 'r', encoding='utf-8') as f:
        buttons_html = f.read().replace('\n', '')

    return buttons_html


def main(bokeh=True, local: str = ''):
    st.set_page_config(page_title=f'{TITLE} - sapp4ua', layout='wide',
                       initial_sidebar_state='auto')

    # Display GitHub Sponsor at top
    buttons_html = header_buttons()
    html(buttons_html, width=600, height=40)

    st.title(TITLE)
    st.markdown(
        '''
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 250px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
           width: 250px;
           margin-left: -250px;
        }
        </style>
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        
        <style>
        footer { visibility: hidden; }
        footer:after {
          content:'Copyright © 2021 Chun Ly. All rights reserved.';
          visibility: visible;
          display: block;
          position: relative;
          text-align: center;
          padding: 5px;
          top: 2px;
        }
        </style>        
        ''',
        unsafe_allow_html=True
    )

    # Load data
    data_dict, unique_df = load_data(local=local)

    # Sidebar, select data view
    view_select = sidebar.select_data_view()

    df = None

    # Sidebar FY selection
    fy_select = ''
    if view_select not in ['About', 'Trends', 'Individual Search']:
        fy_select = sidebar.select_fiscal_year()

        # Select dataframe
        df = data_dict[fy_select]
        st.sidebar.text(f"{fy_select} data imported!")

    # Select pay rate conversion
    pay_norm = 1  # Default: Annual = 1.0
    if view_select not in ['About', 'Highest Earners']:
        pay_norm = sidebar.select_pay_conversion(
            fy_select, pay_norm, view_select
        )

    if view_select == 'About':
        views.about_page()

    if view_select == 'Trends':
        views.trends_page(data_dict, pay_norm)

    if view_select == 'Salary Summary':
        views.salary_summary_page(df, pay_norm, bokeh=bokeh)

    if view_select == 'Highest Earners':
        views.highest_earners_page(df)

    # Select by College Name
    if view_select == 'College/Division Data':
        views.subset_select_data_page(df, COLLEGE_NAME, 'college',
                                      pay_norm, bokeh=bokeh)

    # Select by Department Name
    if view_select == 'Department Data':
        views.subset_select_data_page(df, 'Department', 'department',
                                      pay_norm, bokeh=bokeh)

    if view_select == 'Individual Search':
        views.individual_search_page(data_dict, unique_df)


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Streamlit script")
    parser.add_argument('--local', default='', help='Local path to specify')
    args = parser.parse_args()

    main(bokeh=True, local=args.local)
