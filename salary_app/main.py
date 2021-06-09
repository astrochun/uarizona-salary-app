#!/usr/bin/env python3

import re
import streamlit as st
from streamlit.components.v1 import html

import pandas as pd
import numpy as np

import altair as alt
from bokeh.plotting import figure
from bokeh.models import PrintfTickFormatter

CURRENCY_NORM = True  # Normalize to $1,000
SALARY_COLUMN = 'Annual Salary at Full FTE'
str_n_employees = 'Number of Employees'
fy_list = ['FY2019-20', 'FY2018-19', 'FY2017-18']

pay_conversion = ['Annual', 'Hourly']

fiscal_hours = {
    'FY2019-20': 2096,
    'FY2018-19': 2080,
    'FY2017-18': 2080,
}


@st.cache
def load_data():

    file_id = {
        'FY2019-20': '1d2l29_T-mOh05bglPlwAFlzeV1PIkRXd',
        'FY2018-19': '1paxrUyW1wZuK3bjSL_L7ckKEC6xslZJe',
        'FY2017-18': '1AnRaPpbRTLVyqdeqe6vkPMYgbNnw9zia',
    }

    data_dict = {}
    for year in fy_list:
        data_dict[year] = pd.read_csv(
            f'https://drive.google.com/uc?id={file_id[year]}'
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
    title = 'University of Arizona Salary Data'

    st.set_page_config(page_title=f'{title} - sapp4ua', layout='wide',
                       initial_sidebar_state='auto')

    # Display GitHub Sponsor at top
    buttons_html = header_buttons()
    html(buttons_html, width=600, height=40)

    st.title(title)
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
        ''',
        unsafe_allow_html=True
    )

    # Load data
    data_dict = load_data()

    # Sidebar, select data view
    st.sidebar.markdown('### Select your data view:')
    views = ['About', 'Trends', 'Salary Summary', 'Highest Earners',
             'College/Division Data', 'Department Data']
    view_select = st.sidebar.selectbox('', views, index=0)

    df = None

    # Sidebar FY selection
    if view_select not in ['About', 'Trends']:
        st.sidebar.markdown('### Select fiscal year:')
        fy_select = st.sidebar.selectbox('', fy_list, index=0)

        # Select dataframe
        df = data_dict[fy_select]
        st.sidebar.text(f"{fy_select} data imported!")

    # Select pay rate conversion
    pay_norm = 1  # Default: Annual = 1.0
    if view_select not in ['About', 'Highest Earners']:
        st.sidebar.markdown('### Select pay rate conversion:')
        conversion_select = st.sidebar.selectbox('', pay_conversion, index=0)
        if conversion_select == 'Hourly':
            if view_select != 'Trends':
                pay_norm = fiscal_hours[fy_select]  # Number of hours per FY
            else:
                pay_norm = 2080  # Number of hours per FY

    if view_select == 'About':
        about_page()

    if view_select == 'Trends':
        trends_page(data_dict, pay_norm)

    if view_select == 'Salary Summary':
        salary_summary_page(df, pay_norm, bokeh=bokeh)

    if view_select == 'Highest Earners':
        highest_earners_page(df)

    # Select by College Name
    if view_select == 'College/Division Data':
        subset_select_data_page(df, 'College Name', 'college',
                                pay_norm, bokeh=bokeh)

    # Select by Department Name
    if view_select == 'Department Data':
        subset_select_data_page(df, 'Department', 'department',
                                pay_norm, bokeh=bokeh)


def get_summary_data(df: pd.DataFrame, pd_loc_dict: dict, style: str,
                     pay_norm: int):
    """Gather pandas describe() dataframe and write to streamlit"""

    if style not in ['summary', 'college', 'department']:
        raise ValueError(f"Incorrect style input: {style}")

    # Include all campus data
    all_sum = (df[SALARY_COLUMN]/pay_norm).describe().rename('All')
    series_list = [all_sum]

    str_pay_norm = "Hourly" if pay_norm != 1 else "Annual"
    # Append college location data
    if 'College Location' in pd_loc_dict:
        st.markdown(f'### Common Statistics ({str_pay_norm}):')
        for key, sel in pd_loc_dict['College Location'].items():
            t_row = (df[SALARY_COLUMN][sel]/pay_norm).describe().rename(key)
            series_list.append(t_row)

    # Append college data
    if 'College List' in pd_loc_dict:
        st.markdown(f'### College/Division Statistics ({str_pay_norm}):')
        for key, sel in pd_loc_dict['College List'].items():
            t_row = (df[SALARY_COLUMN][sel]/pay_norm).describe().rename(key)
            series_list.append(t_row)
    else:
        # Append department data for individual department selection
        if 'Department List' in pd_loc_dict:
            st.markdown(f'### Department Statistics ({str_pay_norm}):')
            for key, sel in pd_loc_dict['Department List'].items():
                t_row = (df[SALARY_COLUMN][sel]/pay_norm).describe().rename(key)
                series_list.append(t_row)

    # Show pandas DataFrame of percentile data
    show_percentile_data(series_list)

    # Show department percentile data by college selection
    if style == 'department' and 'College List' in pd_loc_dict:
        for key in pd_loc_dict['College List']:
            st.write(f'Departments in {key}')
            sel = df['College Name'] == key

            dept_list = sorted(df['Department'][sel].unique())
            series_list = []
            for d in dept_list:
                d_sel = df['Department'] == d
                t_row = (df[SALARY_COLUMN][d_sel]/pay_norm).describe().rename(d)
                series_list.append(t_row)

            show_percentile_data(series_list)


def show_percentile_data(series_list):
    summary_df = pd.concat(series_list, axis=1).transpose()
    summary_df.columns = [s.replace('count', 'N') for
                          s in summary_df.columns]
    summary_df.N = summary_df.N.astype(int)
    fmt_dict = {'N': "{:d}"}
    for col in ['mean', 'std', 'min', '25%', '50%', '75%', 'max']:
        fmt_dict[col] = "${:,.2f}"
    st.write(summary_df.style.format(fmt_dict))


def about_page():
    st.markdown("""
    Welcome!
    
    This site was developed to allow easy extraction, analysis, and interpretation of
    salary data from the University of Arizona. It is built and maintained by one volunteer,
    [Chun Ly](https://astrochun.github.io).
    
    This code is built purely with open-source software, specifically
    [`python`](https://python.org), [`streamlit`](https://streamlit.io/), and
    [`pandas`](https://pandas.pydata.org/).
    
    The source code is available
    [here on GitHub!](https://github.com/astrochun/uarizona-salary-app)

    If you have suggestions or encounter an issue, please feel free to submit an
    issue request [here on GitHub](https://github.com/astrochun/uarizona-salary-app/issues)!

    As this is open source, we welcome contributions by
    [forking](https://github.com/astrochun/uarizona-salary-app/fork) the repository, and
    submitting a pull request!
    
    This app was developed because I felt it was an important issue that
    requires greater transparency. I maintain and develop this in my free
    time. With additional data, I hope to extend this application's
    resources.
    
    If you would like to support this project, consider making
    a small monetary contribution either through GitHub (button at the top) or
    [PayPal.Me](https://paypal.me/astrochun).

    You can begin your data journey by selecting a "data view" on the sidebar.
    
    Enjoy!

    Chun 🌵
    """, unsafe_allow_html=True)


def trends_page(data_dict: dict, pay_norm: int = 1):
    """Load Trends page

    :param data_dict: Dictionary containing DataFrame for each FY
    :param pay_norm: Flag indicate type of normalization.
           Annual = 1, Otherwise, it's number of working hours based on FY
    """

    str_pay_norm = "hourly rate" if pay_norm != 1 else "FTE salary"

    trends_list = ['General', 'Income Bracket']
    trends_checkbox = st.sidebar.checkbox(f'Show all trends', True)
    if trends_checkbox:
        trends_select = trends_list
    else:
        trends_select = st.sidebar.multiselect('Select your trends', trends_list)

    stats_list = [
        'Number of employees',
        'Full-time equivalents (FTEs)',
        'Number of part-time employees',
        'Salary budget',
        f'Average {str_pay_norm}',
        f'Median {str_pay_norm}',
        f'Minimum {str_pay_norm}',
        f'Maximum {str_pay_norm}',
    ]

    # Include employee number by income brackets
    income_brackets = [30000, 50000, 100000, 200000, 400000]  # Salary bracket
    norm = 'year'
    if pay_norm != 1:
        income_brackets = [15, 25, 50, 100, 200]  # Hourly bracket
        norm = 'hr'
    income_direction = ['below', 'below', 'above', 'above', 'above']

    bracket_list = [f'Number of employees {dir} ${ib:,d}/{norm}' for
                    ib, dir in zip(income_brackets, income_direction)]

    table_columns = list(data_dict.keys().__reversed__())
    trends_df = pd.DataFrame(columns=table_columns)
    bracket_df = pd.DataFrame(columns=table_columns)

    for fy in data_dict:
        df = data_dict[fy]
        fy_norm = 1 if pay_norm == 1 else fiscal_hours[fy]

        s_col = df[SALARY_COLUMN]/fy_norm
        value_list = [
            df.shape[0], df['FTE'].sum(), df.loc[df['FTE'] < 1].shape[0],
            int(df['Annual Salary at Employment FTE'].sum()),
            s_col.mean(), s_col.median(), s_col.min(), s_col.max(),
        ]

        str_list = [
            f"{value_list[0]:,d}", f"{value_list[1]:,.2f}", f"{value_list[2]:,d}",
            f"${value_list[3]:,d}",
            f"${value_list[4]:,.2f}", f"${value_list[5]:,.2f}",
            f"${value_list[6]:,.2f}", f"${value_list[7]:,.2f}",
        ]
        trends_df[fy] = str_list

        value_list2 = [len(s_col.loc[s_col <= ib]) for ib in income_brackets]
        percent_list2 = [v/value_list[0] * 100 for v in value_list2]

        str_list2 = [
            f"{value_list2[0]:,d} ({percent_list2[0]:.1f}%)",
            f"{value_list2[1]:,d} ({percent_list2[1]:.1f}%)",
            f"{value_list2[2]:,d} ({percent_list2[2]:.1f}%)",
            f"{value_list2[3]:,d} ({percent_list2[3]:.1f}%)",
            f"{value_list2[4]:,d} ({percent_list2[4]:.1f}%)",
        ]
        bracket_df[fy] = str_list2

    trends_df.index = stats_list
    bracket_df.index = bracket_list

    if 'General' in trends_select:
        st.write('## General Statistical Trends')
        st.write(trends_df)

    if 'Income Bracket' in trends_select:
        st.write('## Income Bracket Statistical Trends')
        st.write(bracket_df)


def salary_summary_page(df: pd.DataFrame, pay_norm: int,
                        bokeh: bool = True):
    bin_size = select_bin_size(pay_norm)

    # Plot summary data by college locations
    location = df['College Location'].unique()
    pd_loc_dict = {
        'College Location': {
            'Main': df['College Location'] == location[0],
            'Arizona Health Sciences': df['College Location'] == location[1]
        }
    }
    get_summary_data(df, pd_loc_dict, 'summary', pay_norm)

    histogram_plot(df, bin_size, pay_norm, bokeh=bokeh)


def highest_earners_page(df, step: int = 25000):
    st.sidebar.markdown('### Enter minimum FTE salary:')
    sal_describe = df[SALARY_COLUMN].describe()
    min_salary = st.sidebar.number_input('',
                                         min_value=int(sal_describe['min']),
                                         max_value=int(sal_describe['max']),
                                         value=500000,
                                         step=step)

    # Select sample
    highest_df = df.loc[df[SALARY_COLUMN] >= min_salary]
    percent = len(highest_df)/len(df) * 100.0
    highest_df = highest_df.sort_values(by=[SALARY_COLUMN],
                                        ascending=False).reset_index()
    ahs_df = highest_df.loc[highest_df['College Location'] ==
                            'Arizona Health Sciences']

    write_str_list = [
        f'Number of employees making at or above ${min_salary:,.2f}: ' +
        f'{len(highest_df)} ({percent:.2f}% of UofA employees)\n',
        f'Number of Arizona Health Sciences employees: {len(ahs_df)}',
    ]

    no_athletics = False
    if 'Athletics' in highest_df.columns:
        athletics_df = highest_df.loc[highest_df['Athletics'] == 'Athletics']
        write_str_list.append(
            f'Number of Athletics employees: {len(athletics_df)}\n'
        )
    else:
        no_athletics = True

    # Provide general statistics
    for g_stat in write_str_list:
        st.write(g_stat)

    # Show highest earner table
    col_order = ['Name', 'Primary Title', SALARY_COLUMN,
                 'Athletics', 'College Location', 'College Name',
                 'Department', 'FTE']
    if no_athletics:
        col_order.remove('Athletics')

    st.write(highest_df[col_order])
    st.markdown(f'''
        TIPS\n
        1. You can click on any column to sort by ascending/descending order\n
        2. Some text have ellipses, you can see the full text by mousing over\n
        ''')


def subset_select_data_page(df, field_name, style, pay_norm, bokeh=True):
    bin_size = select_bin_size(pay_norm)

    dept_list = []
    in_selection = []
    pd_loc_dict = dict()

    # Shows selection box for Colleges
    if field_name == 'College Name':
        college_list = sorted(df[field_name].unique())
        college_checkbox = \
            st.checkbox(f'Select all {len(college_list)} colleges/divisions', True)
        college_select = college_list
        if not college_checkbox:
            college_select = st.multiselect(
                'Choose at least one College/Division', college_list)

        if len(college_select) > 0:
            pd_loc_dict['College List'] = \
                {college: df[field_name] == college for
                 college in college_select}

            in_selection = df[field_name].isin(college_select)

    # Shows selection boxes for Departments
    if field_name == 'Department':
        # Shows selection box for college or department approach
        sel_method = st.selectbox(
            'Select by College/Division or individual Department(s)',
            ['College/Division', 'Department'])

        # Populate dept list by college selection
        if sel_method == 'College/Division':
            college_select = st.multiselect(
                f'Choose at least one {sel_method}',
                sorted(df['College Name'].unique()))
            college_select = sorted(college_select)

            pd_loc_dict['College List'] = \
                {college: df['College Name'] == college for
                 college in college_select}

            sel = df['College Name'].isin(college_select)
            dept_list = sorted(df[field_name].loc[sel].unique())

        # Populate dept list by college selection
        if sel_method == 'Department':
            dept_list = st.multiselect(f'Choose at least one {sel_method}',
                                       sorted(df[field_name].unique()))

        if len(dept_list) > 0:
            in_selection = df[field_name].isin(dept_list)
            pd_loc_dict['Department List'] = \
                {entry: df[field_name] == entry for entry in dept_list}

    if len(in_selection) > 0:
        get_summary_data(df, pd_loc_dict, style, pay_norm)

        coll_data = df[in_selection]
        histogram_plot(coll_data, bin_size, pay_norm, bokeh=bokeh)


def bin_data(bin_size: int, pay_norm: int, min_val: float = 10000,
             max_val: float = 2.5e6):

    bins = np.arange(min_val/pay_norm, max_val/pay_norm, bin_size)
    if CURRENCY_NORM and pay_norm == 1:
        bins /= 1e3
    return bins


def select_bin_size(pay_norm: int) -> int:
    st.sidebar.markdown('### Select salary bin size')
    if pay_norm == 1:
        bin_size = st.sidebar.selectbox('', ['$1,000', '$2,500', '$5,000', '$10,000'],
                                        index=2)
    else:
        bin_size = st.sidebar.selectbox('', ['$0.50', '$1.25', '$2.50', '$5.00'],
                                        index=2)

    bin_size = float(re.sub('[$,]', '', bin_size))
    return bin_size


def histogram_plot(data, bin_size, pay_norm: int, bokeh=True):

    bins = bin_data(bin_size, pay_norm)

    x_buffer = 1000 / pay_norm
    x_limit = 500000 / pay_norm
    sal_data = (data[SALARY_COLUMN]/pay_norm).copy()
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
                         x_label=x_label, y_label=str_n_employees,
                         x_range=x_range)
    else:
        bokeh_histogram(salary_bin[:-1], N_bin, pay_norm,
                        x_label=x_label, y_label=str_n_employees,
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

    data_dict[str_n_employees] = y
    salary_df = pd.DataFrame(data_dict)
    tooltip = [SALARY_COLUMN, str_n_employees]

    alt_x = alt.X(f'{SALARY_COLUMN}:Q',
                  scale=alt.Scale(domain=x_range, nice=False))
    c = alt.Chart(salary_df).mark_bar().encode(
        alt_x, y=str_n_employees, tooltip=tooltip).interactive()
    st.altair_chart(c, use_container_width=True)


if __name__ == '__main__':
    main(bokeh=True)
