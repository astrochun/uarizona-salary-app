from typing import Dict

import pandas as pd


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
