import pandas as pd
import streamlit as st

from constants import SALARY_COLUMN, COLLEGE_NAME


def get_summary_data(df: pd.DataFrame, pd_loc_dict: dict, style: str,
                     pay_norm: int):
    """Gather pandas describe() dataframe and write to streamlit"""

    if style not in ['summary', 'college', 'department']:
        raise ValueError(f"Incorrect style input: {style}")

    # Include all campus data
    all_sum = (df[SALARY_COLUMN] / pay_norm).describe().rename('All')
    series_list = [all_sum]

    str_pay_norm = "Hourly" if pay_norm != 1 else "Annual"
    # Append college location data
    if 'College Location' in pd_loc_dict:
        st.markdown(f'### Common Statistics ({str_pay_norm}):')
        for key, sel in pd_loc_dict['College Location'].items():
            t_row = (df[SALARY_COLUMN][sel] / pay_norm).describe().rename(key)
            series_list.append(t_row)

    # Append college data
    if 'College List' in pd_loc_dict:
        st.markdown(f'### College/Division Statistics ({str_pay_norm}):')
        for key, sel in pd_loc_dict['College List'].items():
            t_row = (df[SALARY_COLUMN][sel] / pay_norm).describe().rename(key)
            series_list.append(t_row)
    else:
        # Append department data for individual department selection
        if 'Department List' in pd_loc_dict:
            st.markdown(f'### Department Statistics ({str_pay_norm}):')
            for key, sel in pd_loc_dict['Department List'].items():
                t_row = (df[SALARY_COLUMN][sel] / pay_norm).describe().rename(key)
                series_list.append(t_row)

    # Show pandas DataFrame of percentile data
    show_percentile_data(series_list)

    # Show department percentile data by college selection
    if style == 'department' and 'College List' in pd_loc_dict:
        for key in pd_loc_dict['College List']:
            st.write(f'Departments in {key}')
            sel = df[COLLEGE_NAME] == key

            dept_list = sorted(df['Department'][sel].unique())
            series_list = []
            for d in dept_list:
                d_sel = df['Department'] == d
                t_row = (df[SALARY_COLUMN][d_sel] / pay_norm).describe().rename(d)
                series_list.append(t_row)

            show_percentile_data(series_list)


def show_percentile_data(series_list: list):
    """Write pandas DataFrame of percentile data"""

    summary_df = pd.concat(series_list, axis=1).transpose()
    summary_df.columns = [s.replace('count', 'N') for
                          s in summary_df.columns]
    summary_df.N = summary_df.N.astype(int)
    fmt_dict = {'N': "{:d}"}
    for col in ['mean', 'std', 'min', '25%', '50%', '75%', 'max']:
        fmt_dict[col] = "${:,.2f}"
    st.write(summary_df.style.format(fmt_dict))