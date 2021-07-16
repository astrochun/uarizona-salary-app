from typing import Tuple, Union

import pandas as pd
from pathlib import Path

SALARY_COLUMNS = ['Annual Salary at Employment FTE',
                  'Annual Salary at Full FTE']
FY_COLUMN = 'Fiscal Year'
SF_COLUMN = 'State Fund Ratio'


def main(filename: str):
    """This is for extraction of Daily Wildcat CSV

    :param filename: Full path for CSV file

    Note need to delete top header manually first
    """

    df = pd.read_csv(filename)

    if FY_COLUMN in df.columns:
        print(f"Dropping {FY_COLUMN} column")
        df = df.drop(columns=[FY_COLUMN])

    # Reformat to float for salary
    df = salary_column_conversion(df, '[\$,]')

    outfile = filename.replace('.csv', '_clean.csv')
    print(f"Writing: {outfile}")
    df.to_csv(outfile, index=False)


def lebauer_table_split(filename: str):
    """
    This here reads in David Le Bauer's table and generates clean tables for
    each fiscal year

    :param filename: Full path for CSV file
    """

    p = Path(filename)
    df = pd.read_csv(filename)

    fiscal_years = sorted(df[FY_COLUMN].unique())

    for fy in fiscal_years:
        out_file = p.parent / f"FY{fy-1}-{fy-2000}_clean.csv"

        df_select = df.loc[df[FY_COLUMN] == fy]
        df_select = df_select.drop(columns=FY_COLUMN)
        df_select.rename(columns={
            ' Salary (Full FTE) ': 'Annual Salary at Full FTE',
            ' Annual Salary (Actual) ': 'Annual Salary at Employment FTE'
        }, inplace=True)

        # Reformat to float for salary
        df_select = salary_column_conversion(df_select, '[\$, "]')

        # Reformat to float for state fund
        df_select = state_fund_column_conversion(df_select)

        print(f"Writing: {out_file}")
        df_select.to_csv(out_file, index=False)


def salary_column_conversion(df: pd.DataFrame, regex: str) -> pd.DataFrame:
    """
    Convert columns of salary that is currency formatted to text

    :param df: Salary pandas dataframe
    :param regex: regex to replace

    :return: pandas dataframe with transformation
    """

    for s_column in SALARY_COLUMNS:
        if s_column in df.columns:
            print(f"Convert {s_column} to float")
            salary_col = df[s_column].replace(regex, '', regex=True). \
                astype(float)
            c_loc = df.columns.get_loc(s_column)  # save location
            df = df.drop(columns=[s_column])
            # Insert at the same location
            df.insert(c_loc, s_column, salary_col)
    return df


def state_fund_column_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Change state fund data format from percentile to decimal

    :param df: Salary pandas dataframe

    :return: pandas dataframe with transformation
    """

    if SF_COLUMN in df.columns:
        print(f"Convert {SF_COLUMN} to float")
        salary_col = df[SF_COLUMN].replace('%', '', regex=True). \
                         astype(float) / 100.0
        c_loc = df.columns.get_loc(SF_COLUMN)  # save location
        df = df.drop(columns=[SF_COLUMN])
        df.insert(c_loc, SF_COLUMN, salary_col)  # Insert at the same location
    return df


def write_file(filename: str, name_list: Union[list, set]):
    """Write list of names to file"""

    with open(filename, 'w') as f:
        for val in name_list:
            f.write(f"{val}\n")


def set_unique_identifier(list_files: list):
    """Set unique identifiers for each person, updating tables"""

    unique_df = pd.DataFrame()
    non_unique_df = pd.DataFrame()

    for ii, filename in enumerate(list_files):
        p = Path(filename)
        print(f"Reading: {p}")
        df = pd.read_csv(p)

        fy = p.name.split('_')[0]

        # Get unique names for current dataframe
        name_list_1, name_list_2 = get_unique_names(filename, df)

        if ii == 0:
            # Initialize with earliest fiscal year data
            unique_df = append_to_df(df, unique_df, name_list_1)
            non_unique_df = append_to_df(df, non_unique_df, name_list_2)

            unique_df['year'] = fy
            # Re-sort by unique names (alphabetically), follow by duplicate names
            '''
            unique_df.sort_values(by=['unique', 'Name'], inplace=True,
                                  ascending=[False, True],
                                  ignore_index=True)
            df['uid'] = list(unique_df.index + 1)
            unique_df['uid'] = list(unique_df.index + 1)
            '''
        else:
            # Get latest unique names match from continuously updated unique_df
            unique_names0 = unique_df['Name']
            non_unique_names0 = non_unique_df['Name']

            # Identify existing unique matches and get list of new matches
            name_list_1_union = set(set(name_list_1) & set(unique_names0))
            name_list_1_new   = set(set(name_list_1) - set(unique_names0))
            write_file(filename.replace('.csv', '_unique_union.txt'), name_list_1_union)
            write_file(filename.replace('.csv', '_unique_new.txt'), name_list_1_new)

            # Check against non-unique
            name_list_1_union2 = set(set(name_list_1) & set(non_unique_names0))
            write_file(filename.replace('.csv', '_unique_union2.txt'), name_list_1_union2)

            print(f"Number of unique records in unique_df: {len(name_list_1_union)}")
            print(f"Number of new unique records: {len(name_list_1_new)}")
            print(f"Number of new unique records that is non-unique of unique_df: {len(name_list_1_union2)}")

            # This is unique names not in unique_df and non_unique_df
            name_list_1_new_clean = set(name_list_1_new - name_list_1_union2)

            if len(name_list_1_union) > 0:
                idx = unique_df['Name'].isin(name_list_1)
                unique_df.loc[idx, 'year'] += f";{fy}"

            # Append to unique_df
            if len(name_list_1_new_clean) > 0:
                print(f"Adding {len(name_list_1_new_clean)} to unique_df ...")
                unique_df = append_to_df(df, unique_df, name_list_1_new_clean,
                                         year=fy)

            '''
            if len(name_list_1_union2) > 0:
                df_merge = pd.merge(df, unique_df.loc[unique_df['Name'].isin(name_list_1_union2)],
                                    how='left', on=['Name'], suffixes=['', '_B'])
                uid_update = df_merge['uid'].notnull()
                print(uid_update)
                df.loc[uid_update, 'uid'] = uid_update'''

            '''
            df['uid'] = list(max(unique_df['uid'] + 1))
            unique_df['uid'] = list(unique_df.index + 1)
            '''

    return unique_df



def append_to_df(df: pd.DataFrame, new_df: pd.DataFrame, name_list_1: list,
                 year: str = ''):
    """Append to dataframe from a list of names"""
    temp_df = df.loc[df['Name'].isin(name_list_1)]
    if year:
        temp_df['year'] = year

    new_df = new_df.append(temp_df, ignore_index=True)
    return new_df


def get_unique_names(filename: str, df: pd.DataFrame) -> Tuple[list, list]:
    """Get unique and non-unique_names"""

    unique_names = df['Name'].value_counts().\
        sort_index(key=lambda x: x.str.lower())

    # Start with single occurrence
    name_list_1 = unique_names.loc[unique_names == 1].index.to_list()
    name_list_2 = unique_names.loc[unique_names >= 2].index.to_list()
    print(f"Number of unique records by name: {len(name_list_1)}")
    print(f"Number of records with duplicate names: {len(name_list_2)}")
    write_file(filename.replace('.csv', '_unique.txt'), name_list_1)
    write_file(filename.replace('.csv', '_nonunique.txt'), name_list_2)

    return name_list_1, name_list_2
