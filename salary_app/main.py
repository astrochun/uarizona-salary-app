import streamlit as st
import pandas as pd
import numpy as np

import altair as alt
from bokeh.plotting import figure

SALARY_COLUMN = 'Annual Salary at Full FTE'
str_n_employees = 'Number of Employees'

@st.cache
def get_data():
    df = pd.read_csv('/Users/cly/Downloads/FY2018-19_clean.csv')
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
    s.vbar(x=x, top=y)
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

    data_load_state = st.text('Loading data...')
    df = get_data()
    data_load_state.text("Done!")

    campuses = st.multiselect(
        'Choose college location', df['College Location'].unique())
    if not campuses:
        st.error("Please select at least one college location.")
        data = df
    else:
        mask_campuses = df['College Location'].isin(campuses)
        data = df[mask_campuses]

    st.subheader(f"Total Number of Employees: {len(data)}")
    st.write(data[SALARY_COLUMN].describe())

    bins = np.arange(10000, 2.5e6, 1000)
    x_range = [bins[0], bins[-1]]
    N_bin, salary_bin = np.histogram(data[SALARY_COLUMN], bins=bins,
                                     range=(bins[0], bins[-1]))

    if not bokeh:
        altair_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                         y_label=str_n_employees, x_range=x_range)
    else:
        bokeh_histogram(salary_bin[:-1], N_bin, x_label=SALARY_COLUMN,
                        y_label=str_n_employees, x_range=x_range)


if __name__ == '__main__':
    main(bokeh=True)
