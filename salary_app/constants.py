TITLE = 'University of Arizona Salary Data'  # Full title of app

CURRENCY_NORM = True  # Normalize to $1,000

# Commonly used DataFrame column names
SALARY_COLUMN = 'Annual Salary at Full FTE'
EMPLOYMENT_COLUMN = 'Annual Salary at Employment FTE'

STR_N_EMPLOYEES = 'Number of Employees'
COLLEGE_NAME = 'College Name'

# Choose between annual/hourly conversion
PAY_CONVERSION = ['Annual', 'Hourly']

# List of fiscal years
FY_LIST = [
    'FY2019-20', 'FY2018-19', 'FY2017-18',
    'FY2016-17 (NEW)', 'FY2014-15 (NEW)',
    'FY2013-14 (NEW)', 'FY2011-12 (NEW)',
]

# Number of fiscal hours per fiscal year
FISCAL_HOURS = {
    'FY2019-20': 2096,
    'FY2018-19': 2080,
    'FY2017-18': 2080,
    'FY2016-17': 2088,
    'FY2015-16': 2096,
    'FY2014-15': 2088,
    'FY2013-14': 2088,
    'FY2011-12': 2088,
}

DATA_VIEWS = [
    'About', 'Wage Growth (NEW)', 'Individual Search', 'Trends',
    'Salary Summary', 'Highest Earners', 'College/Division Data',
    'Department Data',
]

# This is for the Trends page
TRENDS_LIST = ['General', 'Income Bracket']

# This is for Individual Search page
INDIVIDUAL_COLUMNS = [
    SALARY_COLUMN, '%', 'FTE', 'Annual Salary at Employment FTE',
    'Primary Title', 'Department', COLLEGE_NAME, 'State Fund Ratio',
]

# This is for Wage Growth page
TITLE_LIST = ['Unchanged', 'Changed', 'Both']

# Inflation data (percentages)
# Source: https://www.bls.gov/data/inflation_calculator.htm
INFLATION_DATA = {
    'FY2019-20': 1.0,  # 07/2019-07/2020
    'FY2018-19': 2.0,  # 07/2018-07/2019
    'FY2017-18': 3.0,  # 07/2017-07/2018
    'FY2016-17': 3.0,  # 07/2015-07/2017
    'FY2014-15': 0.0,  # 07/2014-07/2015
    'FY2013-14': 4.0,  # 07/2012-07/2014
}