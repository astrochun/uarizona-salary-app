import pandas as pd
import streamlit as st

import sidebar
from constants import FISCAL_HOURS, SALARY_COLUMN, COLLEGE_NAME, INDIVIDUAL_COLUMNS
from plots import histogram_plot
from commons import get_summary_data, format_salary_df


def about_page():
    st.markdown("""
    Welcome 🤙 !

    **TL;DR:**<br>
    _This is a website providing public salary data for the University of
    Arizona. It is a "Choose Your Own Data Science" (CYODS) tool, so just
    explore with different "data views" on the sidebar!_

    **More information:**<br>
    This site was developed to allow easy extraction, analysis, and interpretation of
    salary data from the University of Arizona.<br>
    It is built and maintained by one volunteer, [Chun Ly](https://astrochun.github.io).

    This code is built purely with open-source software, specifically
    [`python`](https://python.org), [`streamlit`](https://streamlit.io/),
    [`bokeh`](https://bokeh.org/), and [`pandas`](https://pandas.pydata.org/).

    The source code is available
    [on GitHub!](https://github.com/astrochun/uarizona-salary-app)

    If you have suggestions or encounter an issue, please feel free to submit an
    issue request [on GitHub](https://github.com/astrochun/uarizona-salary-app/issues)!

    As this is open source, we welcome contributions by
    [forking](https://github.com/astrochun/uarizona-salary-app/fork) the repository, and
    submitting a pull request!

    This app was developed because I felt it was an important issue that
    requires greater transparency.<br>
    I maintain and develop this in my free time. With additional data, I hope to extend
    this application's resources.

    You can begin your data journey by selecting a "data view" on the sidebar:
    
     1. Trends 🆕 : General facts and numbers (e.g. number of employees,
        salary budget, etc.), for each fiscal year
     2. Salary Summary: Statistics and percentile salary data, includes salary histogram
     3. Highest Earners: Extract data above a minimum salary
     4. College/Division Data: Similar to Salary Summary but extracted for each college(s)/division(s)
     4. Department Data: Similar to Salary Summary but extracted for each department(s)

    Enjoy!<br>
    &#8208; Chun 🌵

    **Sponsorship:**<br>
    If you find this website beneficial, please consider making a small
    monetary donation either through GitHub (button at the top) or
    [PayPal.Me](https://paypal.me/astrochun). This support ensures that
    this project will:

    1. Grow to provide more data, tools, and visualizations, and
    2. Continue to be an open-source transparent resource for our community.

    _I have offered nearly 70 hours of my free time within the first 45 days
    to make all of this happen._<br>
    _Your donations will be highlighted below._

    This project has been sponsored by these gracious folks:

    _Continued donors_:

    1. [Casper da Costa-Luis](https://cdcl.ml/)

    _One-time donors_:

    1. Sedona Heidinger

    **Sources:**<br>
    The salary data are made available from the [The Daily WildCat](https://www.wildcat.arizona.edu/).
    Links are available for:

     1. [FY2019-20](https://docs.google.com/spreadsheets/d/e/2PACX-1vTaAWak0pN6Jnulm95eTM7kIubvNNMPgYh3d6sCHN5W1tekpIktoMBoDKJeZhmAyI7ZzH1BAytEp_bV/pubhtml)
        (Google Sheets). Extracted and converted to a machine-readable version by Michael Clarkson.
     2. [FY2018-19](https://docs.google.com/spreadsheets/d/1d2wLowmL5grmsqTj-qFg2ke9k--s1gN_oEZ6kstSX6c/edit#gid=0) (Google Sheets)
     3. [FY2017-18](https://docs.google.com/spreadsheets/d/1jFmxbDx6FP5qk5KKbFBJ5RvS0R2_HEoCkaw83P_DUG0/edit#gid=2006091355) (Google Sheets)
     4. FY2011-12, FY2013-14, FY2014-15, FY2015-16, FY2016-17:
        These data were made available by Dr. David Le Bauer, obtained from
        older records from The Daily Wildcat (Google Sheets are currently not available/public)
    """, unsafe_allow_html=True)


def trends_page(data_dict: dict, pay_norm: int = 1):
    """Load Trends page

    :param data_dict: Dictionary containing DataFrame for each FY
    :param pay_norm: Flag indicate type of normalization.
           Annual = 1, Otherwise, it's number of working hours based on FY
    """

    str_pay_norm = "hourly rate" if pay_norm != 1 else "FTE salary"

    trends_select = sidebar.select_trends()

    stats_list = [
        'No. of employees',
        'Full-time equivalents',
        'No. of part-time empl.',
        f'Salary budget ({"annual" if pay_norm == 1 else "hourly"})',
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

    bracket_list = [f'No. empl. {dir} ${ib:,d}/{norm}' for
                    ib, dir in zip(income_brackets, income_direction)]

    table_columns = list(data_dict.keys().__reversed__())
    trends_df = pd.DataFrame(columns=table_columns)
    bracket_df = pd.DataFrame(columns=table_columns)

    last_year_value = []
    for i, fy in enumerate(table_columns):
        df = data_dict[fy]
        fy_norm = 1 if pay_norm == 1 else FISCAL_HOURS[fy]

        s_col = df[SALARY_COLUMN] / fy_norm
        value_list = [
            df.shape[0], df['FTE'].sum(), df.loc[df['FTE'] < 1].shape[0],
            int(df['Annual Salary at Employment FTE'].sum())/fy_norm,
            s_col.mean(), s_col.median(), s_col.min(), s_col.max(),
        ]

        if i == 0:
            percent_list = [''] * len(value_list)
        else:
            percent_list = [f'({(a-b)/b * 100.0:+04.1f}%)' for a, b in
                            zip(value_list, last_year_value)]

        str_list = [
            f"{value_list[0]:,d} {percent_list[0]}",
            f"{value_list[1]:,.2f} {percent_list[1]}",
            f"{value_list[2]:,d} {percent_list[2]}",
            f"${value_list[3]:,.2f} {percent_list[3]}",
            f"${value_list[4]:,.2f} {percent_list[4]}",
            f"${value_list[5]:,.2f} {percent_list[5]}",
            f"${value_list[6]:,.2f} {percent_list[6]}",
            f"${value_list[7]:,.2f} {percent_list[7]}",
        ]
        trends_df[fy] = str_list

        value_list2 = \
            [len(s_col.loc[s_col <= ib]) for ib in income_brackets[0:2]] + \
            [len(s_col.loc[s_col >= ib]) for ib in income_brackets[2:]]

        percent_list2 = [v/value_list[0] * 100 for v in value_list2]

        str_list2 = [
            f"{value_list2[0]:,d} ({percent_list2[0]:04.1f}%)",
            f"{value_list2[1]:,d} ({percent_list2[1]:04.1f}%)",
            f"{value_list2[2]:,d} ({percent_list2[2]:04.1f}%)",
            f"{value_list2[3]:,d} ({percent_list2[3]:04.1f}%)",
            f"{value_list2[4]:,d} ({percent_list2[4]:04.1f}%)",
        ]
        bracket_df[fy] = str_list2

        last_year_value = value_list.copy()

    trends_df.index = stats_list
    bracket_df.index = bracket_list

    if 'General' in trends_select:
        st.write('## General Statistical Trends')
        st.write(trends_df)
        st.write("Percentages are against previous year's data.")

    if 'Income Bracket' in trends_select:
        st.write('## Income Bracket Statistical Trends')
        st.write(bracket_df)
        st.write("Percentages are relative to total number of employees for a given year.")


def individual_search_page(data_dict: dict, unique_df: pd.DataFrame):
    """Search tool page for individuals

    :param data_dict: Dictionary containing DataFrame for each FY
    :param unique_df: DataFrame with unique names
    """

    st.write("""
    You can search across multiple fiscal years for a number of individuals""")

    list_names = unique_df['Name']
    names_select = st.multiselect('', list_names)

    fmt_dict = {'N': "{:d}"}
    for col in ['mean', 'std', 'min', '25%', '50%', '75%', 'max']:
        fmt_dict[col] = "${:,.2f}"

    for name in sorted(names_select):
        st.write(f"**Records for: {name}**")

        uid_df = unique_df.loc[unique_df['Name'].isin([name])]
        uid = uid_df['uid'].values[0]

        in_fy_list = uid_df['year'].values[0].split(';')

        record_df = pd.DataFrame()  # index=in_fy_list)
        for fy in in_fy_list:
            t_df = data_dict[fy]
            record = t_df.loc[t_df['uid'] == uid]
            record_df = record_df.append(record)
        record_df.index = in_fy_list

        # If common data across year, show above table
        select_individual_columns = INDIVIDUAL_COLUMNS.copy()
        for common_field in ['Primary Title', 'Department', COLLEGE_NAME]:
            cf_values = record_df.loc[
                record_df[common_field].notnull(), common_field].unique()
            if len(cf_values) == 1:
                st.write(f"{common_field}: {cf_values[0]}")
                select_individual_columns.remove(common_field)

        # Only show columns with non-unique results across year
        format_salary_df(record_df[select_individual_columns])


def salary_summary_page(df: pd.DataFrame, pay_norm: int,
                        bokeh: bool = True):
    """
    Load Salary Summary page

    :param df: DataFrame for viewing
    :param pay_norm: Normalization constant for hourly/annual
    :param bokeh: Boolean to use Bokeh. Default: True
    """

    bin_size = sidebar.select_bin_size(pay_norm)

    # Plot summary data by college locations
    # Fix handling for different college locations, including null case
    location = df['College Location'].dropna().unique()
    pd_loc_dict = {
        'College Location': {
            loc: df['College Location'] == loc for loc in location
        }
    }
    if len(location) > 0:
        if not df.loc[df['College Location'].isnull()].empty:
            pd_loc_dict['College Location']['N/A'] = \
                df['College Location'].isnull()

    get_summary_data(df, pd_loc_dict, 'summary', pay_norm)

    histogram_plot(df, bin_size, pay_norm, bokeh=bokeh)


def highest_earners_page(df, step: int = 25000):
    """
    Load Highest Earners page

    :param df: DataFrame for viewing
    :param step: Step-size for +/- for manual changes via clicks
    """

    min_salary = sidebar.select_minimum_salary(df, step)

    # Select sample
    highest_df = df.loc[df[SALARY_COLUMN] >= min_salary]
    percent = len(highest_df)/len(df) * 100.0
    highest_df = highest_df.sort_values(by=[SALARY_COLUMN],
                                        ascending=False).reset_index()

    write_str_list = [
        f'Number of employees making at or above ${min_salary:,.2f}: ' +
        f'{len(highest_df)} ({percent:.2f}% of UofA employees)\n'
    ]

    ahs_df = highest_df.loc[
        (highest_df['College Location'] == 'Arizona Health Sciences') |
        (highest_df['College Location'] == 'AHSC')]
    if len(ahs_df) > 0:
        write_str_list.append(
            f'Number of Arizona Health Sciences employees: {len(ahs_df)}'
        )

    no_athletics = False
    if 'Athletics' in highest_df.columns:
        athletics_df = highest_df.loc[highest_df['Athletics'] == 'Athletics']
        if len(athletics_df) > 0:
            write_str_list.append(
                f'Number of Athletics employees: {len(athletics_df)}\n'
            )
        else:
            no_athletics = True
    else:
        no_athletics = True

    # Provide general statistics
    for g_stat in write_str_list:
        st.write(g_stat)

    # Show highest earner table
    col_order = ['Name', 'Primary Title', SALARY_COLUMN,
                 'Athletics', 'College Location', COLLEGE_NAME,
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
    """
    Show College/Division Data or Department Data page

    :param df: DataFrame for viewing
    :param field_name: String indicating view. Options are:
           'College Name' or 'Department'
    :param style: String describing the style for plots.
           Options are summary, college, department
    :param pay_norm: Normalization constant for hourly/annual
    :param bokeh: Boolean to use Bokeh. Default: True
    """

    bin_size = sidebar.select_bin_size(pay_norm)

    dept_list = []
    in_selection = []
    pd_loc_dict = dict()

    college_list = sorted(df[COLLEGE_NAME].dropna().unique())

    # Shows selection box for Colleges
    if field_name == COLLEGE_NAME:
        if len(college_list) > 0:
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
        else:
            st.error("""
            Unfortunately the current available data for this fiscal year does
            not include College information. As such, you cannot select by
            College/Division. This will hopefully get resolved when I get
            the full data. Stay tuned my patient data scientist!""")

    # Shows selection boxes for Departments
    if field_name == 'Department':
        # Shows selection box for college or department approach
        if len(college_list) > 0:
            sel_method = st.selectbox(
                'Select by College/Division or individual Department(s)',
                ['College/Division', 'Department'])
        else:
            sel_method = st.selectbox(
                'Select by individual Department(s)',
                ['Department'])

        # Populate dept list by college selection
        if sel_method == 'College/Division':
            college_select = st.multiselect(
                f'Choose at least one {sel_method}', college_list)
            college_select = sorted(college_select)

            pd_loc_dict['College List'] = \
                {college: df[COLLEGE_NAME] == college for
                 college in college_select}

            sel = df[COLLEGE_NAME].isin(college_select)
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
