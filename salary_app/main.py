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


def bokeh_histogram(x, y, x_label: str, y_label: str,
                    x_range: list, title: str = '',
                    bc: str = "#f0f0f0", bfc: str = "#fafafa"):

    s = figure(title=title,
               x_axis_label=x_label,
               y_axis_label=y_label,
               x_range=x_range,
               background_fill_color=bc,
               border_fill_color=bfc,
               tools=["xpan,xwheel_zoom,xzoom_in,xzoom_out,save,reset"])
    s.vbar(x=x, top=y, width=0.95*1e3)
    st.bokeh_chart(s, use_container_width=True)


def altair_histogram(x, y, x_label: str, y_label: str,
                     x_range: list, title: str = ''):

    data_dict=dict()
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

    st.markdown('### Select fiscal year:')
    fy_select = st.selectbox('',
                             ['FY2018-19', 'FY2017-18'],
                             index=0)

    data_load_state = st.text('Loading data...')
    df = get_data(fy_select)
    data_load_state.text("Data loaded!", )

    location = df['College Location'].unique()
    main_df = df.loc[df['College Location'] == location[0]]
    ahs_df = df.loc[df['College Location'] == location[1]]

    # Pandas data summary for salary
    st.markdown('### Summary:')
    get_summary_data(ahs_df, df, location, main_df)

    bins = np.arange(10000, 2.5e6, 1000)
    x_range = [bins[0], 500000]  # bins[-1]]
    N_bin, salary_bin = np.histogram(df[SALARY_COLUMN], bins=bins,
                                     range=(bins[0], bins[-1]))

    if not bokeh:
        altair_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                         y_label=str_n_employees, x_range=x_range)
    else:
        bokeh_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                        y_label=str_n_employees, x_range=x_range)

    # Select by College Name
    st.markdown('### Choose a College:')
    colleges = st.multiselect('', sorted(df['College Name'].unique()))
    if not colleges:
        st.error("Please select at least one college name.")
    else:
        mask_campuses = df['College Name'].isin(colleges)
        coll_data = df[mask_campuses]

        N_bin, salary_bin = np.histogram(coll_data[SALARY_COLUMN], bins=bins)
        x_range = [min(coll_data[SALARY_COLUMN])-1000,
                   max(coll_data[SALARY_COLUMN])+1000]
        if not bokeh:
            altair_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                             y_label=str_n_employees, x_range=x_range)
        else:
            bokeh_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                            y_label=str_n_employees, x_range=x_range)


def get_summary_data(ahs_df: pd.DataFrame,
                     df: pd.DataFrame,
                     location: list,
                     main_df: pd.DataFrame):
    """Gather pandas describe() dataframe and write to streamlit"""

    all_sum = df[SALARY_COLUMN].describe().rename('All')
    main_sum = main_df[SALARY_COLUMN].describe().rename(location[0])
    ahs_sum = ahs_df[SALARY_COLUMN].describe().rename(location[1])
    summary_df = pd.concat([all_sum, main_sum, ahs_sum], axis=1).transpose()
    summary_df.columns = [s.replace('count', 'N') for s in summary_df.columns]
    summary_df.N = summary_df.N.astype(int)
    fmt_dict = {'N': "{:d}"}
    for col in ['mean', 'std', 'min', '25%', '50%', '75%', 'max']:
        fmt_dict[col] = "${:,.2f}"
    st.write(summary_df.style.format(fmt_dict))


if __name__ == '__main__':
    main(bokeh=True)
