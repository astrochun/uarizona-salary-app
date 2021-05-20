#!/usr/bin/env python3

import re
import streamlit as st
import pandas as pd
import numpy as np

import altair as alt
from bokeh.plotting import figure

SALARY_COLUMN = 'Annual Salary at Full FTE'
str_n_employees = 'Number of Employees'
fy_list = ['FY2018-19', 'FY2017-18']


@st.cache
def load_data():

    data_dict = {}
    for year in fy_list:
        data_dict[year] = pd.read_csv(f'/Users/cly/Downloads/{year}_clean.csv')

    return data_dict


def main(bokeh=True):
    st.title('University of Arizona Salary Data')

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
        ''',
        unsafe_allow_html=True
    )

    # Load data
    data_dict = load_data()

    # Sidebar FY selection
    st.sidebar.markdown('### Select fiscal year:')
    fy_select = st.sidebar.selectbox('', fy_list, index=0)

    # Select dataframe
    df = data_dict[fy_select]
    st.sidebar.text(f"{fy_select} data imported!")

    # Sidebar, select data view
    st.sidebar.markdown('### Select your data view:')
    views = ['About', 'Salary Summary', 'Highest Earners',
             'College/Division Data', 'Department Data']
    view_select = st.sidebar.selectbox('', views, index=0)

    if view_select == 'About':
        about_page()

    if view_select == 'Salary Summary':
        salary_summary_page(df, bokeh=bokeh)

    if view_select == 'Highest Earners':
        highest_earners_page(df)

    # Select by College Name
    if view_select == 'College/Division Data':
        subset_select_data_page(df, 'College Name', 'college', bokeh=bokeh)

    # Select by Department Name
    if view_select == 'Department Data':
        subset_select_data_page(df, 'Department', 'department', bokeh=bokeh)


def get_summary_data(df: pd.DataFrame, pd_loc_dict: dict, style: str):
    """Gather pandas describe() dataframe and write to streamlit"""

    if style not in ['summary', 'college', 'department']:
        raise ValueError(f"Incorrect style input: {style}")

    # Include all campus data
    all_sum = df[SALARY_COLUMN].describe().rename('All')
    series_list = [all_sum]

    # Append college location data
    if 'College Location' in pd_loc_dict:
        st.markdown(f'### Common Statistics:')
        for key, sel in pd_loc_dict['College Location'].items():
            t_row = df[SALARY_COLUMN][sel].describe().rename(key)
            series_list.append(t_row)

    # Append college data
    if 'College List' in pd_loc_dict:
        st.markdown(f'### College/Division Statistics:')
        for key, sel in pd_loc_dict['College List'].items():
            t_row = df[SALARY_COLUMN][sel].describe().rename(key)
            series_list.append(t_row)
    else:
        # Append department data for individual department selection
        if 'Department List' in pd_loc_dict:
            st.markdown(f'### Department Statistics:')
            for key, sel in pd_loc_dict['Department List'].items():
                t_row = df[SALARY_COLUMN][sel].describe().rename(key)
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
                t_row = df[SALARY_COLUMN][d_sel].describe().rename(d)
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
    issue request [here on GitHub!](https://github.com/astrochun/uarizona-salary-app/issues).

    As this is open source, we welcome contributions by
    [forking](https://github.com/astrochun/uarizona-salary-app/fork) the repository, and
    submitting a pull request!
    
    This app was developed because I felt it was an important issue that requires
    greater transparency. I maintain and develop this in free time. If you like,
    consider making a small contribution to supporting this project.
    """)


def salary_summary_page(df: pd.DataFrame, bokeh: bool = True):
    bin_size = select_bin_size()

    # Plot summary data by college locations
    location = df['College Location'].unique()
    pd_loc_dict = {
        'College Location': {
            'Main': df['College Location'] == location[0],
            'Arizona Health Sciences': df['College Location'] == location[1]
        }
    }
    get_summary_data(df, pd_loc_dict, 'summary')

    histogram_plot(df, bin_size, bokeh=bokeh)


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
    athletics_df = highest_df.loc[highest_df['Athletics'] == 'Athletics']
    ahs_df = highest_df.loc[highest_df['College Location'] ==
                            'Arizona Health Sciences']

    # Provide general statistics
    st.write(f'''
        Number of employees making at or above ${min_salary:,.2f}:
        {len(highest_df)} ({percent:.2f}% of UofA employees)\n
        Number of Athletics employees: {len(athletics_df)}\n
        Number of Arizona Health Sciences employees: {len(ahs_df)}
        ''')

    # Show highest earner table
    col_order = ['Name', 'Primary Title', SALARY_COLUMN,
                 'Athletics', 'College Location', 'College Name',
                 'Department', 'FTE']
    st.write(highest_df[col_order])
    st.markdown(f'''
        TIPS\n
        1. You can click on any column to sort by ascending/descending order\n
        2. Some text have ellipses, you can see the full text by mousing over\n
        ''')


def subset_select_data_page(df, field_name, style, bokeh=True):
    bin_size = select_bin_size()

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
        get_summary_data(df, pd_loc_dict, style)

        coll_data = df[in_selection]
        histogram_plot(coll_data, bin_size, bokeh=bokeh)


def bin_data(bin_size: int, min_val: float = 10000, max_val: float = 2.5e6):
    return np.arange(min_val, max_val, bin_size)


def select_bin_size() -> int:
    st.sidebar.markdown('### Select salary bin size')
    bin_size = st.sidebar.selectbox('', ['$1,000', '$2,500', '$5,000', '$10,000'],
                                    index=2)
    bin_size = int(re.sub('[$,]', '', bin_size))
    return bin_size


def histogram_plot(data, bin_size, bokeh=True):

    bins = bin_data(bin_size)
    N_bin, salary_bin = np.histogram(data[SALARY_COLUMN], bins=bins)
    x_range = [min(bins) - 1000,
               min([max(data[SALARY_COLUMN]) + 1000, 500000])]
    if not bokeh:
        altair_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                         y_label=str_n_employees, x_range=x_range)
    else:
        bokeh_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                        y_label=str_n_employees, x_range=x_range)


def bokeh_histogram(x, y, x_label: str, y_label: str,
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
    st.bokeh_chart(s, use_container_width=True)


def altair_histogram(x, y, x_label: str, y_label: str,
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
