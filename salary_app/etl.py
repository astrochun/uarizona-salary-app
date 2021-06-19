import pandas as pd
from pathlib import Path

SALARY_COLUMNS = ['Annual Salary at Employment FTE',
                  'Annual Salary at Full FTE']
FY_COLUMN = 'Fiscal Year'


def main(filename: str):
    # Note need to delete top header manually first

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

        print(f"Writing: {out_file}")
        df_select.to_csv(out_file, index=False)


def salary_column_conversion(df: pd.DataFrame, regex: str):
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

