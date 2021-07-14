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


def write_file(filename: str, name_list: list):
    """Write list of names to file"""

    with open(filename, 'w') as f:
        for val in name_list:
            f.write(f"{val}\n")


def set_unique_identifier(list_files: list):
    """Set unique identifiers for each person, updating tables"""

    unique_df = pd.DataFrame()

    for ii, filename in enumerate(list_files):
        print(f"Reading: {filename}")
        df = pd.read_csv(filename)

        # Initialize with earliest fiscal year data
        if ii == 0:
            unique_df = unique_df.append(df, ignore_index=True)
            unique_df['unique'] = False

        # Get unique names
        unique_names = df['Name'].value_counts().\
            sort_index(key=lambda x: x.str.lower())

        # Start with single occurrence
        name_list_1 = unique_names.loc[unique_names == 1].index.to_list()
        name_list_2 = unique_names.loc[unique_names >= 2].index.to_list()

        if ii == 0:
            unique_df.loc[unique_df['Name'].isin(name_list_1), 'unique'] = True
            # Re-sort to use indexing as unique identifier
            unique_df.sort_values(by=['unique', 'Name'], inplace=True,
                                  ascending=[False, True],
                                  ignore_index=True)
            df['uid'] = list(unique_df.index + 1)
            unique_df['uid'] = list(unique_df.index + 1)

