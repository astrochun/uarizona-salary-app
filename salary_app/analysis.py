from typing import Dict

import pandas as pd
from scipy.stats import binned_statistic
import streamlit as st


def match_by_name(data_dict: Dict[str, pd.DataFrame], fy_current: str,
                  fy_old: str) -> pd.DataFrame:
    """
    Match by name to get comparison of salary

    :param data_dict: Dictionary of DataFrame for each fiscal year
    :param fy_current: Selected fiscal year
    :param fy_old: Previous fiscal year

    :return: DataFrame with contents merged by Name field
    """

    data_dict.keys()
    df_current = data_dict[fy_current].copy()
    df_old = data_dict[fy_old].copy()

    # Rename columns
    # cols = df_old.columns[1:]
    # print(cols)
    # ['Primary Title', 'Annual Salary at Employment FTE', 'FTE',
    #  'Annual Salary at Full FTE', 'State Fund Ratio']
    # df_old = df_old.rename(columns=dict(zip(cols, [f"{c} old" for c in cols])))

    #df_combine = pd.merge(df_current, df_old, how='left',
    #                      on=['Name', 'Department'])
    df_merge = pd.merge(df_current, df_old, how='left',
                        on=['Name', 'Department'], suffixes=('_A', '_B'))
    df_merge['Annual Salary at Full FTE_B'].fillna(df_old['Annual Salary at Full FTE'], inplace=True)

    return df_merge


def compute_bin_averages(salary_arr: list, percent_arr: list, index, bins):

    mean_stat, bin_edges, binnumber = \
        binned_statistic(salary_arr[index], percent_arr[index],
                         statistic='mean', bins=bins,
                         range=[10, 2400])

    median_stat, bin_edges, binnumber = \
        binned_statistic(salary_arr[index], percent_arr[index],
                         statistic='median', bins=bins,
                         range=[10, 2400])

    max_stat, bin_edges, binnumber = \
        binned_statistic(salary_arr[index], percent_arr[index],
                         statistic='max', bins=bins,
                         range=[10, 2400])

    count_stats, bin_edges, binnumber = \
        binned_statistic(salary_arr[index], percent_arr[index],
                         statistic='count', bins=bins,
                         range=[10, 2400])

    d = {
        'Salary range': [f"${int(bin_edges[i]):,} - {int(bin_edges[i+1]):,}k"
                         for i in range(len(bin_edges[:-1]))],
        'bin': [(bin_edges[i] + bin_edges[i+1])/2
                for i in range(len(bin_edges[:-1]))],
        'N': count_stats,
        'median %': median_stat,
        'mean %': mean_stat,
        'max %': max_stat,
    }

    stats_df = pd.DataFrame(data=d)

    return stats_df
