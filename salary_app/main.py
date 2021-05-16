import re
import streamlit as st
import pandas as pd
import numpy as np

import altair as alt
from bokeh.plotting import figure

SALARY_COLUMN = 'Annual Salary at Full FTE'
str_n_employees = 'Number of Employees'


@st.cache
def get_data(year_str):
    df = pd.read_csv(f'/Users/cly/Downloads/{year_str}_clean.csv')
    return df


def bin_data(bin_size: int, min_val: float = 10000, max_val: float = 2.5e6):
    return np.arange(min_val, max_val, bin_size)


def select_bin_size() -> float:
    st.sidebar.markdown('### Select salary bin size')
    bin_size = st.sidebar.selectbox('', ['$1,000', '$2,500', '$5,000', '$10,000'],
                                    index=2)
    bin_size = float(re.sub('[$,]', '', bin_size))
    return bin_size


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
               tools=["xpan,xwheel_zoom,xzoom_in,xzoom_out,save,reset"])
    s.vbar(x=x, top=y, width=0.95*bin_size)
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
    # Sidebar FY selection
    st.sidebar.markdown('### Select fiscal year:')
    fy_select = st.sidebar.selectbox('',
                                     ['FY2018-19', 'FY2017-18'],
                                     index=0)

    data_load_state = st.sidebar.text('Loading data...')
    df = get_data(fy_select)
    data_load_state.text("Data loaded!", )

    st.sidebar.markdown('### Select your data view:')
    views = ['Salary Summary', 'Highest Earners', 'College Data',
             'Department Data']
    view_select = st.sidebar.selectbox('', views, index=0)

    if view_select == 'Salary Summary':
        salary_summary_page(df, bokeh=bokeh)

    if view_select == 'Highest Earners':
        highest_earners_page(df)

    # Select by College Name
    if view_select == 'College Data':
        subset_select_data_page(df, 'College Name', bokeh=bokeh)

    # Select by Department Name
    if view_select == 'Department Data':
        subset_select_data_page(df, 'Department', bokeh=bokeh)


def get_summary_data(df: pd.DataFrame, pd_loc_dict: dict):
    """Gather pandas describe() dataframe and write to streamlit"""

    all_sum = df[SALARY_COLUMN].describe().rename('All')
    series_list = [all_sum]
    for key in pd_loc_dict:
        t_row = df[SALARY_COLUMN][pd_loc_dict[key]].describe().rename(key)
        series_list.append(t_row)

    summary_df = pd.concat(series_list, axis=1).transpose()
    summary_df.columns = [s.replace('count', 'N') for s in summary_df.columns]
    summary_df.N = summary_df.N.astype(int)
    fmt_dict = {'N': "{:d}"}
    for col in ['mean', 'std', 'min', '25%', '50%', '75%', 'max']:
        fmt_dict[col] = "${:,.2f}"
    st.write(summary_df.style.format(fmt_dict))


def salary_summary_page(df: pd.DataFrame, bokeh: bool = True):
    st.markdown(f'### Common Statistics:')

    bin_size = select_bin_size()

    location = df['College Location'].unique()
    pd_loc_dict = {
        'Main': df['College Location'] == location[0],
        'Arizona Health Sciences': df['College Location'] == location[1]
    }

    get_summary_data(df, pd_loc_dict)

    bins = bin_data(bin_size)
    x_range = [bins[0], 500000]  # bins[-1]]
    N_bin, salary_bin = np.histogram(df[SALARY_COLUMN], bins=bins,
                                     range=(bins[0], bins[-1]))

    if not bokeh:
        altair_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                         y_label=str_n_employees, x_range=x_range)
    else:
        bokeh_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                        y_label=str_n_employees, x_range=x_range)


def highest_earners_page(df):
    st.sidebar.markdown('### Enter a minimum full-time salary:')
    try:
        min_salary = float(st.sidebar.text_input('', 500000))

        highest_df = df.loc[df[SALARY_COLUMN] >= min_salary]
        percent = len(highest_df)/len(df) * 100.0
        highest_df = highest_df.sort_values(by=[SALARY_COLUMN],
                                            ascending=False).reset_index()
        athletics_df = highest_df.loc[highest_df['Athletics'] == 'Athletics']
        ahs_df = highest_df.loc[highest_df['College Location'] == 'Arizona Health Sciences']

        st.write(f'''
            Number of employees making at or above ${min_salary:,.2f}:
            {len(highest_df)} ({percent:.2f}% of UofA employees)\n
            Number of Athletics employees: {len(athletics_df)}\n
            Number of Arizona Health Sciences employees: {len(ahs_df)}
            ''')
        col_order = ['Name', 'Primary Title', SALARY_COLUMN,
                     'Athletics', 'College Location', 'College Name', 'Department',
                     'FTE']
        st.write(highest_df[col_order])
        st.markdown(f'''
            TIPS\n
            1. You can click on any column to sort by ascending/descending order\n
            2. Some text have ellipses, you can see the full text by mousing over\n
            ''')
    except ValueError:
        st.sidebar.error('Please enter a numerical value!')


def subset_select_data_page(df, field_name, bokeh=True):
    bin_size = select_bin_size()

    field_list = st.multiselect('Choose at least one',
                                sorted(df[field_name].unique()))
    if not field_list:
        st.error("Please select at least one!")
    else:
        st.markdown(f'### Common Statistics:')

        in_selection = df[field_name].isin(field_list)
        coll_data = df[in_selection]

        pd_loc_dict = dict()
        for entry in field_list:
            pd_loc_dict[entry] = df[field_name] == entry

        get_summary_data(df, pd_loc_dict)

        bins = bin_data(bin_size)
        N_bin, salary_bin = np.histogram(coll_data[SALARY_COLUMN], bins=bins)
        x_range = [min(bins) - 1000,
                   max(coll_data[SALARY_COLUMN]) + 1000]
        if not bokeh:
            altair_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                             y_label=str_n_employees, x_range=x_range)
        else:
            bokeh_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                            y_label=str_n_employees, x_range=x_range)


if __name__ == '__main__':
    main(bokeh=True)
