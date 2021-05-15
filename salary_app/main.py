import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

SALARY_COLUMN = 'Annual Salary at Full FTE'
str_n_employees = 'Number of Employees'

st.title('University of Arizona Salary Data')


@st.cache
def get_data():
    df = pd.read_csv('/Users/cly/Downloads/FY2018-19_clean.csv')
    return df


def main():
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
    hist_values = np.histogram(data[SALARY_COLUMN], bins=bins,
                               range=(bins[0], bins[-1]))
    data_dict = dict()
    data_dict[SALARY_COLUMN] = hist_values[1][:-1]
    data_dict[str_n_employees] = hist_values[0]
    salary_df = pd.DataFrame(data_dict)
    tooltip = [SALARY_COLUMN, str_n_employees]

    alt_x = alt.X(f'{SALARY_COLUMN}:Q',
                  scale=alt.Scale(domain=[bins[0], bins[-1]], nice=False))
    c = alt.Chart(salary_df).mark_bar().encode(
        alt_x, y=str_n_employees, tooltip=tooltip).interactive()
    st.altair_chart(c, use_container_width=True)


if __name__ == '__main__':
    main()

