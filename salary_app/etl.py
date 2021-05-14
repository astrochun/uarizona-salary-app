import pandas as pd

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
