import re

import streamlit as st

from constants import DATA_VIEWS, FY_LIST, PAY_CONVERSION, FISCAL_HOURS, \
    TRENDS_LIST, SALARY_COLUMN


def select_data_view() -> str:
    """Sidebar widget to select your data view"""

    st.sidebar.markdown('### Select your data view:')
    view_select = st.sidebar.selectbox('', DATA_VIEWS, index=0). \
        replace(' (NEW)', '')

    return view_select


def select_fiscal_year() -> str:
    """Sidebar widget to select fiscal year"""

    st.sidebar.markdown('### Select fiscal year:')
    fy_select = st.sidebar.selectbox('', FY_LIST, index=0).split(' ')[0]

    return fy_select


def select_pay_conversion(fy_select, pay_norm, view_select) -> int:
    """Sidebar widget to select pay rate conversion (hourly/annual)"""

    st.sidebar.markdown('### Select pay rate conversion:')
    conversion_select = st.sidebar.selectbox('', PAY_CONVERSION, index=0)
    if conversion_select == 'Hourly':
        if view_select != 'Trends':
            pay_norm = FISCAL_HOURS[fy_select]  # Number of hours per FY
        else:
            pay_norm = 2080  # Number of hours per FY

    return pay_norm


def select_trends() -> str:
    """Sidebar widget to select trends for Trends page"""

    trends_checkbox = st.sidebar.checkbox(f'Show all trends', True)
    if trends_checkbox:
        trends_select = TRENDS_LIST
    else:
        trends_select = st.sidebar.multiselect('Select your trends', TRENDS_LIST)

    return trends_select


def select_minimum_salary(df, step):
    """Sidebar widget to select minimum salary for Highest Earners page"""

    st.sidebar.markdown('### Enter minimum FTE salary:')
    sal_describe = df[SALARY_COLUMN].describe()
    min_salary = st.sidebar.number_input('',
                                         min_value=100000,
                                         max_value=int(sal_describe['max']),
                                         value=500000,
                                         step=step)

    return min_salary


def select_bin_size(pay_norm: int) -> float:
    """Sidebar widget to select salary bin size for histogram plots"""

    st.sidebar.markdown('### Select salary bin size')
    if pay_norm == 1:
        bin_size = st.sidebar.selectbox('', ['$1,000', '$2,500', '$5,000', '$10,000'],
                                        index=2)
    else:
        bin_size = st.sidebar.selectbox('', ['$0.50', '$1.25', '$2.50', '$5.00'],
                                        index=2)

    bin_size = float(re.sub('[$,]', '', bin_size))

    return bin_size
