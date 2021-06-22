#!/usr/bin/env python3

import streamlit as st
from streamlit.components.v1 import html

import pandas as pd
import numpy as np

import altair as alt
from bokeh.plotting import figure
from bokeh.models import PrintfTickFormatter, Label

from constants import CURRENCY_NORM, SALARY_COLUMN, STR_N_EMPLOYEES, \
    COLLEGE_NAME, FY_LIST, TITLE
import sidebar
import views


@st.cache
def load_data():

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
        data_dict[year.split(' ')[0]] = pd.read_csv(
            f'https://drive.google.com/uc?id={file_id[year.split(" ")[0]]}'
        )

    return data_dict


@st.cache
def header_buttons() -> str:
    """Return white-background version of GitHub Sponsor button"""
    file_name = "assets/header_buttons.html"
    with open(file_name, 'r', encoding='utf-8') as f:
        buttons_html = f.read().replace('\n', '')

    return buttons_html


def main(bokeh=True):
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
    data_dict = load_data()

    # Sidebar, select data view
    view_select = sidebar.select_data_view()

    df = None

    # Sidebar FY selection
    if view_select not in ['About', 'Trends']:
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


def bin_data(bin_size: int, pay_norm: int, min_val: float = 10000,
             max_val: float = 2.5e6):

    bins = np.arange(min_val/pay_norm, max_val/pay_norm, bin_size)
    if CURRENCY_NORM and pay_norm == 1:
        bins /= 1e3
    return bins


def histogram_plot(data, bin_size, pay_norm: int, bokeh=True):

    bins = bin_data(bin_size, pay_norm)

    x_buffer = 1000 / pay_norm
    x_limit = 500000 / pay_norm
    sal_data = (data[SALARY_COLUMN] / pay_norm).copy()
    if CURRENCY_NORM and pay_norm == 1:
        sal_data /= 1e3
        x_buffer /= 1e3
        x_limit /= 1e3

    if pay_norm == 1:
        x_label = SALARY_COLUMN
    else:
        x_label = 'Hourly Rate'

    N_bin, salary_bin = np.histogram(sal_data, bins=bins)
    x_range = [min(bins) - x_buffer,
               min([max(sal_data) + x_buffer, x_limit])]
    if not bokeh:
        altair_histogram(salary_bin[:-1], N_bin, pay_norm,
                         x_label=x_label, y_label=STR_N_EMPLOYEES,
                         x_range=x_range)
    else:
        bokeh_histogram(salary_bin[:-1], N_bin, pay_norm,
                        x_label=x_label, y_label=STR_N_EMPLOYEES,
                        x_range=x_range)


def bokeh_histogram(x, y, pay_norm, x_label: str, y_label: str,
                    x_range: list, title: str = '',
                    bc: str = "#f0f0f0", bfc: str = "#fafafa"):

    bin_size = x[1] - x[0]

    s = figure(title=title,
               x_axis_label=x_label,
               y_axis_label=y_label,
               x_range=x_range,
               background_fill_color=bc,
               border_fill_color=bfc,
               tools=["xpan,xwheel_zoom,xzoom_in,xzoom_out,save,reset"]
               )

    # Add copyright
    l1 = Label(x=5, y=9, text_font_size='10px', x_units='screen',
               y_units='screen',
               text='Copyright © 2021 Chun Ly. https://sapp4ua.herokuapp.com.  '
                    'Figure: CC BY 4.0.  Code: MIT')
    s.add_layout(l1)

    s.vbar(x=x, top=y, width=0.95*bin_size, fill_color="#f8b739",
           fill_alpha=0.5, line_color=None)
    if CURRENCY_NORM and pay_norm == 1:
        s.xaxis[0].formatter = PrintfTickFormatter(format="$%ik")
    else:
        s.xaxis[0].formatter = PrintfTickFormatter(format="$%i")
    st.bokeh_chart(s, use_container_width=True)


def altair_histogram(x, y, pay_norm, x_label: str, y_label: str,
                     x_range: list, title: str = ''):

    data_dict = dict()
    data_dict[SALARY_COLUMN] = x

    data_dict[STR_N_EMPLOYEES] = y
    salary_df = pd.DataFrame(data_dict)
    tooltip = [SALARY_COLUMN, STR_N_EMPLOYEES]

    alt_x = alt.X(f'{SALARY_COLUMN}:Q',
                  scale=alt.Scale(domain=x_range, nice=False))
    c = alt.Chart(salary_df).mark_bar().encode(
        alt_x, y=STR_N_EMPLOYEES, tooltip=tooltip).interactive()
    st.altair_chart(c, use_container_width=True)


if __name__ == '__main__':
    main(bokeh=True)
