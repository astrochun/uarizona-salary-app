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

    for s_column in SALARY_COLUMNS:
        if s_column in df.columns:
            print(f"Convert {s_column} to float")
            salary_col = df[s_column].replace('[\$,]', '', regex=True).\
                astype(float)
            c_loc = df.columns.get_loc(s_column)  # save location
            df = df.drop(columns=[s_column])
            # Insert at the same location
            df.insert(c_loc, s_column, salary_col)

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

    fy_column = 'Fiscal Year'
    fiscal_years = sorted(df[fy_column].unique())

    for fy in fiscal_years:
        out_file = p.parent / f"FY{fy-1}-{fy-2000}_clean.csv"

        df_select = df.loc[df[fy_column] == fy]
        df_select = df_select.drop(columns=fy_column)
        df_select.rename(columns={
            ' Salary (Full FTE) ': 'Annual Salary at Full FTE',
            ' Annual Salary (Actual) ': 'Annual Salary at Employment FTE'
        }, inplace=True)
        print(f"Writing: {out_file}")
        df_select.to_csv(out_file, index=False)
