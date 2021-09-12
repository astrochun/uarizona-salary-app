from time import sleep

import numpy as np
import pandas as pd
import streamlit as st

import sidebar
from constants import FISCAL_HOURS, SALARY_COLUMN, COLLEGE_NAME, \
    INDIVIDUAL_COLUMNS, FY_LIST, CURRENCY_NORM
from plots import histogram_plot, bokeh_scatter, bokeh_scatter_init
from commons import get_summary_data, format_salary_df, show_percentile_data
from analysis import compute_bin_averages


def about_page():
    st.markdown("""
    Welcome 🤙 !

    **TL;DR:**<br>
    _This is a website providing public salary data for the University of
    Arizona. It is a "Choose Your Own Data Science" tool, so just
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
    
     1. **Wage Growth 🆕 : Year-to-year salary changes**
     2. Individual Search: Find all salary data for individual(s) or by department
     2. Trends: General facts and numbers (e.g. number of employees,
        salary budget, etc.), for each fiscal year
     3. Salary Summary: Statistics and percentile salary data, includes salary histogram
     4. Highest Earners (Updated): Extract data above a minimum salary. Now you can select a given college/division
     5. College/Division Data: Similar to Salary Summary but extracted for each college(s)/division(s)
     6. Department Data: Similar to Salary Summary but extracted for each department(s)

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
    to make all of this happen. Your donations will be highlighted below._

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
    """Search tool page for individuals and by department

    :param data_dict: Dictionary containing DataFrame for each FY
    :param unique_df: DataFrame with unique names
    """

    st.write("""
    You can search across multiple fiscal years for a number of individuals.
    Use the search method on the left to do:

    1. Individual search (multiple names supported)
    2. Department search (individual department)

    Search tips:
    
    1. For individual search, enter the full name as "LastName,FirstName"
    2. For department search, enter its acronym or part of the department's name
    """)

    list_names = unique_df['Name']

    search_method = sidebar.select_search_method()

    # Initialize
    names_select = []
    sort_alpha = False

    if search_method == 'Individual':
        st.markdown("Select/enter names of individuals:")
        names_select = st.multiselect('', list_names)

        sort_alpha = \
            st.checkbox(f'Sort results alphabetically by last name', True)

    if search_method == 'Department':
        # Select from most recent available fiscal year, sort by salary
        recent_df: pd.DataFrame = data_dict[FY_LIST[0]].sort_values(
            by=SALARY_COLUMN, ascending=False)
        dept_names: list = sorted(recent_df['Department'].unique().tolist())
        initial_query = dept_names.index('Office of the Provost')

        st.markdown("Select a department:")
        dept_select = st.selectbox('', dept_names, index=initial_query)

        # Get names within department that has a UID (N=1 case)
        dept_match_df = recent_df.loc[(recent_df['Department'] == dept_select) &
                                      (recent_df['uid'].notnull())]

        sort_select = sidebar.select_sort_method()
        if sort_select == 'Alphabetically':
            sort_alpha = True

        names_select = dept_match_df['Name'].tolist()

        st.info(f"{len(names_select)} records found!")

        describe_df = dept_match_df[SALARY_COLUMN].describe()
        show_percentile_data([describe_df], no_count=True)

        progress_bar = st.progress(0)
        sleep(0.5)

    if sort_alpha:
        names_select.sort()

    for i, name in enumerate(names_select, 1):
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

        select_individual_columns = INDIVIDUAL_COLUMNS.copy()

        # Add year-to-year change
        if len(record_df) > 1:
            salary_arr = record_df[SALARY_COLUMN].values
            percent = ['']
            percent += [f'{x:.1f}' for x in (salary_arr[1:] / salary_arr[0:-1] - 1.0) * 100.]
            record_df.insert(len(record_df.columns), '%', percent)
        else:
            select_individual_columns.remove('%')

        # If common data across year, show above table
        for common_field in ['Primary Title', 'Department', COLLEGE_NAME]:
            cf_values = record_df.loc[
                record_df[common_field].notnull(), common_field].unique()
            if len(cf_values) == 1:
                st.write(f"{common_field}: {cf_values[0]}")
                select_individual_columns.remove(common_field)

        # Only show columns with non-unique results across year
        format_salary_df(record_df[select_individual_columns])
        if search_method == 'Department':
            progress_bar.progress(i/len(names_select))


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

    st.write('Choose across campus or College/Division')
    select_method = st.selectbox('', ['Entire University', 'College/Division'],
                                 index=0)

    college_select = ''
    if select_method == 'College/Division':
        step = 5000  # Change step size

        college_list = sorted(df[COLLEGE_NAME].dropna().unique())

        # Shows selection box for Colleges
        if len(college_list) > 0:
            college_select = st.selectbox(
                'Choose one College/Division', college_list)
        else:
            st.error("""
            Unfortunately the current available data for this fiscal year does
            not include College information. As such, you cannot select by
            College/Division. This will hopefully get resolved when I get
            the full data. Stay tuned my patient data scientist!""")
            return

    min_salary = sidebar.select_minimum_salary(df, step, college_select)

    # Select sample
    if select_method == 'College/Division':
        df_ref = df.loc[df[COLLEGE_NAME] == college_select]
        str_ref = college_select
    else:
        df_ref = df.copy()
        str_ref = 'UofA'

    highest_df = df_ref.loc[df[SALARY_COLUMN] >= min_salary]

    percent = len(highest_df)/len(df_ref) * 100.0
    highest_df = highest_df.sort_values(by=[SALARY_COLUMN],
                                        ascending=False).reset_index()

    write_str_list = [
        f'Number of {str_ref} employees making at or above ${min_salary:,.2f}: ' +
        f'{len(highest_df)} ({percent:.2f}% of {str_ref} employees)\n'
    ]

    if len(highest_df['College Location'].unique()) > 1:
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

    if select_method == 'College/Division':
        col_order.remove(COLLEGE_NAME)

    format_salary_df(highest_df[col_order])

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


def wage_growth_page(data_dict: dict, fy_select: str,
                     pay_norm, bokeh=True):
    """
    Show wage growth plots

    :param data_dict:
    :param fy_select:
    :param pay_norm: Normalization constant for hourly/annual
    :param bokeh: Boolean to use Bokeh. Default: True
    """

    st.write(f"""
    This data view provides year-to-year growth against the previous year.
    You can select the fiscal year of interest on the sidebar.

    This plot is *interactive* - you can mouse over any data point to
    identify individual(s)

    Employees are distinguished in two categories:

    1. Unchanged: Those who did not have a change in their job title
    2. Changed: Those who had a title change. The latter could either
       be due to a career change, a promotion (e.g., Assistant Professor
       to Associate Professor), or a "step down" (e.g., Interim Dean to
       Associate Professor)
    """)

    # Get selected year
    df = data_dict[fy_select]

    df = df.loc[df['uid'].notnull()]

    # Get previous year
    list_fy = list(data_dict)
    prev_year = list_fy[list_fy.index(fy_select)+1]
    df_old = data_dict[prev_year]
    df_old = df_old.loc[df_old['uid'].notnull()]

    result_df = df.merge(df_old, how='inner', suffixes=['_A', '_B'], on=['uid'])

    s_col = result_df[f'{SALARY_COLUMN}_A'] / pay_norm
    percent = (result_df[f'{SALARY_COLUMN}_A'] /
               result_df[f'{SALARY_COLUMN}_B'] - 1) * 100
    if CURRENCY_NORM and pay_norm == 1:
        s_col /= 1e3

    bin_size = sidebar.select_bin_size(pay_norm, index=3)

    select_pts = sidebar.select_by_title()

    same_title = result_df.loc[result_df['Primary Title_A'] ==
                               result_df['Primary Title_B']].index

    title_changed = result_df.loc[result_df['Primary Title_A'] !=
                                  result_df['Primary Title_B']].index

    n_same = len(same_title)
    n_changed = len(title_changed)

    p_same = 100 * n_same / (n_changed + n_same)
    p_changed = 100 * n_changed / (n_changed + n_same)

    st.markdown(f"""
    <div style="text-align:center; font-size:14pt">
      <table style="display: inline-table">
      <tr style="border: 0px">
        <td style="border: 0px"><b>Unchanged</b></td>
        <td style="border: 0px"><b>Changed</b></td>
      </tr>
      <tr style="border: 0px">
        <td style="border: 0px">{len(same_title)} ({p_same:.1f}%)</td>
        <td style="border: 0px">{len(title_changed)} ({p_changed:.1f}%)</td>
      </tr>
      </table>
    </div>
    """, unsafe_allow_html=True)

    percentiles = np.arange(0.1, 1.0, 0.1)
    all_percent_df = percent.describe(percentiles=percentiles).rename('All')
    series_list = [all_percent_df]

    same_title_percent_df = percent[same_title].describe(percentiles=percentiles).rename('Unchanged')
    series_list.append(same_title_percent_df)

    changed_percent_df = percent[title_changed].describe(percentiles=percentiles).rename('Changed')
    changed_percent_df.rename('Changed')
    series_list.append(changed_percent_df)
    show_percentile_data(series_list, no_count=True, table_format="{:,.2f}%")

    if bokeh:
        s = bokeh_scatter_init(pay_norm, x_label=SALARY_COLUMN,
                               y_label='Percentage')

        if select_pts in ['Unchanged', 'Both']:
            s = bokeh_scatter(s_col[same_title], percent[same_title],
                              result_df.loc[same_title, 'Name_A'], fc='white',
                              s=s)
            compute_bin_averages(s_col, percent, same_title, bin_size,
                                 pay_norm)

        if select_pts in ['Changed', 'Both']:
            s = bokeh_scatter(s_col[title_changed], percent[title_changed],
                              result_df.loc[title_changed, 'Name_A'],
                              fc='purple', s=s)
            compute_bin_averages(s_col, percent, title_changed, bin_size,
                                 pay_norm)

        st.bokeh_chart(s, use_container_width=True)
