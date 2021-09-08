import re

import streamlit as st

from constants import DATA_VIEWS, FY_LIST, PAY_CONVERSION, FISCAL_HOURS, \
    TRENDS_LIST, SALARY_COLUMN, COLLEGE_NAME, TITLE_LIST


def select_data_view() -> str:
    """Sidebar widget to select your data view"""

    st.sidebar.markdown('### Select your data view:')
    view_select = st.sidebar.selectbox('', DATA_VIEWS, index=0). \
        replace(' (NEW)', '')

    return view_select


def select_fiscal_year(view_select) -> str:
    """Sidebar widget to select fiscal year"""

    if 'Wage Growth' in view_select:
        working_fy_list = FY_LIST[:-1]
    else:
        working_fy_list = FY_LIST

    st.sidebar.markdown('### Select fiscal year:')
    fy_select = st.sidebar.selectbox('', working_fy_list, index=0).split(' ')[0]

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


def select_minimum_salary(df, step, college_select: str = ''):
    """Sidebar widget to select minimum salary for Highest Earners page"""

    st.sidebar.markdown('### Enter minimum FTE salary:')
    sal_describe = df[SALARY_COLUMN].describe()

    number_input_settings = {
        'min_value': 100000,
        'max_value': int(sal_describe['max']),
        'value': 500000,
        'step': step
    }

    if college_select:
        t_df = df.loc[df[COLLEGE_NAME] == college_select]
        sal_describe = t_df[SALARY_COLUMN].describe()
        max_value = int(sal_describe['max'])
        number_input_settings['max_value'] = max_value

        if max_value > 100000:
            number_input_settings['min_value'] = 75000
            number_input_settings['value'] = 100000
        else:
            number_input_settings['min_value'] = 65000
            number_input_settings['value'] = 75000

    min_salary = st.sidebar.number_input('', **number_input_settings)

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


def select_search_method():
    """Sidebar widget to identify search method for individual search page"""
    st.sidebar.markdown('### Search method:')
    search_method = st.sidebar.selectbox('', ['Individual', 'Department'], index=0)
    return search_method


def select_sort_method():
    """Sidebar widget to indicate sorting method"""
    st.sidebar.markdown('### Sort method:')
    sort_select = st.sidebar.selectbox('', ['Alphabetically', 'FTE Salary'],
                                       index=1)
    return sort_select


def select_by_title():
    """Sidebar widget to select by title change status"""

    st.sidebar.markdown('### Select job title status:')
    select_pts = st.sidebar.selectbox('', TITLE_LIST, index=0)

    return select_pts
